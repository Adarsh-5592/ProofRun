import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


MANAGED_LABEL = "proofrun.managed=true"
DEFAULT_STALE_SECONDS = 300


def docker_command(args, timeout=15):
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def find_stale_containers(older_than):
    result = docker_command([
        "ps", "-aq",
        "--filter", f"label={MANAGED_LABEL}",
    ])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Docker query failed")

    container_ids = result.stdout.splitlines()
    now = datetime.now(timezone.utc)
    stale = []

    for container_id in container_ids:
        inspection = docker_command(["inspect", container_id])

        if inspection.returncode != 0:
            print(f"Could not inspect {container_id}: {inspection.stderr.strip()}")
            continue

        try:
            container = json.loads(inspection.stdout)[0]
            created = datetime.fromisoformat(
                container["Created"].replace("Z", "+00:00")
            )
            age = (now - created).total_seconds()
            status = container["State"]["Status"]

            # Never automatically remove potentially active containers.
            safe_to_remove = status in {"created", "exited", "dead"}

            if age >= older_than and safe_to_remove:
                stale.append({
                    "id": container["Id"],
                    "name": container["Name"].lstrip("/"),
                    "status": status,
                    "age": int(age),
                })

        except (KeyError, IndexError, ValueError, json.JSONDecodeError):
            print(f"Invalid inspection data for {container_id}")

    return stale


def main():
    parser = argparse.ArgumentParser(
        description="Find and optionally remove stale ProofRun containers."
    )
    parser.add_argument(
        "--older-than",
        type=int,
        default=DEFAULT_STALE_SECONDS,
        help="Minimum container age in seconds (default: 300).",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Actually remove stale containers. Without this, only preview.",
    )

    args = parser.parse_args()

    if args.older_than < 1:
        parser.error("--older-than must be at least 1 second")

    try:
        stale = find_stale_containers(args.older_than)

        if not stale:
            print("No stale ProofRun containers found.")
            return 0

        print(f"Found {len(stale)} stale ProofRun container(s):")

        for item in stale:
            print(
                f"- {item['name']} | "
                f"status={item['status']} | "
                f"age={item['age']}s | "
                f"id={item['id'][:12]}"
            )

        if not args.delete:
            print("\nDRY RUN: No containers were removed.")
            print("Use --delete to remove these containers.")
            return 0

        failures = 0

        for item in stale:
            removal = docker_command(
                ["rm", "--force", item["id"]],
                timeout=15,
            )

            if removal.returncode == 0:
                print(f"Removed: {item['name']}")
            else:
                failures += 1
                print(
                    f"Failed to remove {item['name']}: "
                    f"{removal.stderr.strip()}"
                )

        print(f"\nCleanup finished. Failures: {failures}")
        return 1 if failures else 0

    except (OSError, subprocess.TimeoutExpired, RuntimeError) as exc:
        print(f"Cleanup error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
