# ProofRun Sandbox Integration

## Module
sandbox/sandbox.py

## Public function
run_code(code: str, timeout_seconds: int = 10) -> dict

## Example
from sandbox.sandbox import run_code

result = run_code(
    code="print(1 + 1)",
    timeout_seconds=10
)

## Result fields
- status
- stdout
- stderr
- exit_code
- timed_out
- output_limited
- duration_ms
- error
- cleanup_ok
- oom_killed
- container_state

## Possible statuses
- success
- error
- timeout
- output_limit
- memory_limit
- sandbox_error
- cleanup_error

## Security restrictions
- Docker network disabled
- Read-only container filesystem
- Non-root execution (UID/GID 10001)
- 128 MB memory limit
- 0.5 CPU limit
- 32 process limit
- 30-second maximum execution timeout
- 1 MB maximum combined output
- 256 KB maximum input code
- Linux capabilities dropped
- No-new-privileges enabled
- Temporary filesystem mounted with noexec
- Container forcibly removed after execution

## Important
The backend must never execute generated Python code directly.
All generated code must pass through run_code().

The sandbox module requires Docker access.
Do not expose the Docker socket to the frontend or generated code.
