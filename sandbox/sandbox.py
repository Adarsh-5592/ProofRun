import json
import os
import selectors
import subprocess
import time
import uuid
import threading


IMAGE = "proofrun-sandbox:1.0"

MAX_CODE_BYTES = 256 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_TIMEOUT = 30
MAX_CONCURRENT_EXECUTIONS = 2
SLOT_WAIT_SECONDS = 1

_execution_slots = threading.BoundedSemaphore(
    MAX_CONCURRENT_EXECUTIONS
)



def _inspect_container_state(container_id: str) -> dict:
    inspection = subprocess.run(
        ["docker", "inspect", "--format={{json .State}}", container_id],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )

    if inspection.returncode != 0:
        raise RuntimeError(
            inspection.stderr.strip() or "Docker state inspection failed"
        )

    try:
        state = json.loads(inspection.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Could not parse Docker container state") from exc

    if not isinstance(state, dict):
        raise RuntimeError("Docker returned an invalid container state")

    return state

def _run_code(code: str, timeout_seconds: int = 10) -> dict:
    started = time.monotonic()

    result = {
        "status": "sandbox_error",
        "stdout": "",
        "stderr": "",
        "exit_code": None,
        "timed_out": False,
        "output_limited": False,
        "duration_ms": 0,
        "error": None,
        "cleanup_ok": True,
        "oom_killed": False,
        "container_state": None,
    }

    if not isinstance(code, str):
        result["error"] = "Code must be a string"
        return result

    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= MAX_TIMEOUT:
        result["error"] = "Timeout must be between 1 and 30 seconds"
        return result

    source = code.encode("utf-8")

    if len(source) > MAX_CODE_BYTES:
        result["error"] = "Code exceeds 256 KB"
        return result

    container_id = None
    container_name = None
    cleanup_target = None

    try:
        name = f"proofrun-{uuid.uuid4().hex[:16]}"
        container_name = name

        create = subprocess.run(
            [
                "docker", "create",
                "--name", name,
                "--label", "proofrun.managed=true",
                "-i",
                "--network=none",
                "--read-only",
                "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777",
                "--memory=128m",
                "--memory-swap=128m",
                "--cpus=0.5",
                "--pids-limit=32",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges:true",
                "--user=10001:10001",
                "--ulimit=core=0",
                "--ulimit=nofile=64:64",
                "--ulimit=fsize=1048576:1048576",
                "--ulimit=cpu=10:10",
                "--workdir=/workspace",
                IMAGE,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

        if create.returncode != 0:
            raise RuntimeError(create.stderr.strip())

        cleanup_target = container_name
        container_id = create.stdout.strip()

        if container_id:
            cleanup_target = container_id

        if not container_id:
            raise RuntimeError("Docker returned no container ID")

        process = subprocess.Popen(
            ["docker", "start", "--attach", "--interactive", container_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        selector = selectors.DefaultSelector()
        stdout_data = bytearray()
        stderr_data = bytearray()

        streams = {
            "stdout": process.stdout,
            "stderr": process.stderr,
        }

        for label, stream in streams.items():
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, label)

        os.set_blocking(process.stdin.fileno(), False)
        selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")

        position = 0
        deadline = time.monotonic() + timeout_seconds

        try:
            while selector.get_map():
                remaining = deadline - time.monotonic()

                if remaining <= 0:
                    result["timed_out"] = True
                    break

                events = selector.select(min(remaining, 0.1))

                for key, _ in events:
                    label = key.data

                    if label == "stdin":
                        try:
                            count = os.write(
                                process.stdin.fileno(),
                                source[position:position + 65536],
                            )
                            position += count

                            if position >= len(source):
                                selector.unregister(process.stdin)
                                process.stdin.close()

                        except BlockingIOError:
                            # The pipe is temporarily full; retry when writable.
                            continue
                        except (BrokenPipeError, OSError):
                            selector.unregister(process.stdin)
                            process.stdin.close()

                    else:
                        try:
                            chunk = os.read(key.fd, 65536)
                        except OSError:
                            chunk = b""

                        if not chunk:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                            continue

                        used = len(stdout_data) + len(stderr_data)
                        available = MAX_OUTPUT_BYTES - used

                        target = stdout_data if label == "stdout" else stderr_data
                        target.extend(chunk[:available])

                        if len(chunk) > available:
                            result["output_limited"] = True
                            break

                if result["output_limited"]:
                    break

        finally:
            selector.close()

            if result["timed_out"] or result["output_limited"]:
                process.kill()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            for stream in (process.stdin, process.stdout, process.stderr):
                if stream and not stream.closed:
                    stream.close()

        result["stdout"] = stdout_data.decode("utf-8", errors="replace")
        result["stderr"] = stderr_data.decode("utf-8", errors="replace")
        result["exit_code"] = process.returncode

        state = _inspect_container_state(container_id)

        result["container_state"] = state.get("Status")
        result["oom_killed"] = bool(state.get("OOMKilled", False))

        if result["timed_out"]:
            result["status"] = "timeout"
        elif result["output_limited"]:
            result["status"] = "output_limit"
        elif result["oom_killed"]:
            result["status"] = "memory_limit"
        elif state.get("Error") or state.get("Status") != "exited":
            result["status"] = "sandbox_error"
            result["error"] = (
                state.get("Error")
                or result["stderr"].strip()
                or "Container did not reach the exited state"
            )
        elif process.returncode == 0:
            result["status"] = "success"
        else:
            result["status"] = "error"

    except FileNotFoundError:
        result["error"] = "Docker executable not found"

    except subprocess.TimeoutExpired:
        result["error"] = "Docker operation timed out"
        if cleanup_target is None:
            cleanup_target = container_id or container_name

    except (OSError, RuntimeError) as exc:
        result["error"] = str(exc)

    finally:
        if cleanup_target:
            try:
                cleanup = subprocess.run(
                    ["docker", "rm", "--force", cleanup_target],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

                missing_container = (
                    "no such container" in cleanup.stderr.lower()
                )

                result["cleanup_ok"] = (
                    cleanup.returncode == 0 or missing_container
                )

                if not result["cleanup_ok"]:
                    result["status"] = "cleanup_error"
                    result["error"] = (
                        cleanup.stderr.strip()
                        or cleanup.stdout.strip()
                        or "Container cleanup failed"
                    )

            except (OSError, subprocess.TimeoutExpired) as exc:
                result["status"] = "cleanup_error"
                result["error"] = str(exc)

        result["duration_ms"] = round(
            (time.monotonic() - started) * 1000
        )

    return result


def run_code(code: str, timeout_seconds: int = 10) -> dict:
    """Run code with a bounded number of concurrent executions."""
    started = time.monotonic()

    if not _execution_slots.acquire(timeout=SLOT_WAIT_SECONDS):
        return {
            "status": "busy",
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "timed_out": False,
            "output_limited": False,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "error": "Sandbox is busy. Please try again shortly.",
            "cleanup_ok": True,
            "oom_killed": False,
            "container_state": None,
        }

    try:
        return _run_code(code, timeout_seconds)
    finally:
        _execution_slots.release()
