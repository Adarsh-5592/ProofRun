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

## Stale Container Cleanup

Module: sandbox/cleanup.py

The cleanup utility identifies abandoned ProofRun containers
that are older than five minutes.

It only considers containers with this label:

proofrun.managed=true

Eligible container states:
- created
- exited
- dead

Running containers are never automatically removed.

### Dry-run

Preview stale containers without deleting anything:

sudo python sandbox/cleanup.py

### Remove stale containers

Deletion requires explicit confirmation through the --delete flag:

sudo python sandbox/cleanup.py --delete

### Custom age threshold

The default threshold is 300 seconds (5 minutes).

Example:

sudo python sandbox/cleanup.py --older-than 600

### Safety guarantees

- Dry-run is the default.
- Only ProofRun-managed containers are considered.
- Recent containers are ignored.
- Running containers are protected.
- Deletion requires the explicit --delete flag.
- Docker errors and cleanup failures are reported.

### Operational note

The cleanup utility is currently a manually invoked recovery tool.
Automatic scheduling and recovery after host restarts must be
configured and verified separately during deployment.

Do not expose Docker daemon access to untrusted users.
