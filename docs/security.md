# ProofRun — Sandbox Security Architecture

## 1. Overview

ProofRun executes AI-generated Python code inside temporary,
isolated Docker containers.

The objective is to prevent untrusted generated code from
accessing the host filesystem, network or unrestricted resources.

## 2. Execution Architecture

1. The backend receives a user task.
2. The AI generates Python code.
3. The backend sends the generated code to sandbox.py.
4. sandbox.py creates a temporary Docker container.
5. The code executes inside the isolated container.
6. Standard output, errors and execution status are collected.
7. The container is forcibly removed after execution.

## 3. Isolation Controls

| Security control | Configuration |
|---|---|
| Container runtime | Docker |
| Execution user | UID/GID 10001 |
| Network | Disabled |
| Root filesystem | Read-only |
| Temporary storage | 16 MB tmpfs |
| Temporary storage execution | noexec |
| Linux capabilities | All dropped |
| Privilege escalation | Disabled |
| Seccomp | Docker default profile |
| Memory | 128 MB |
| Memory + swap limit | 128 MB |
| CPU quota | 0.5 CPU |
| Process limit | 32 |
| Core dumps | Disabled |
| File size limit | 1 MB |
| CPU time limit | 10 seconds |
| Working directory | /workspace |

## 4. Execution Limits

| Limit | Value |
|---|---|
| Maximum input code | 256 KB |
| Maximum combined output | 1 MB |
| Default execution timeout | 10 seconds |
| Maximum execution timeout | 30 seconds |

## 5. Error Handling

The sandbox reports structured execution statuses:

- success
- error
- timeout
- output_limit
- memory_limit
- sandbox_error
- cleanup_error

Docker container state is inspected to distinguish
memory exhaustion from ordinary Python errors.

## 6. Container Lifecycle

- Every execution receives a unique container name.
- Containers are created with the proofrun.managed=true label.
- Containers are removed forcibly after execution.
- Cleanup failures are reported separately.
- The container name is retained as a fallback cleanup target.

## 7. Automated Security Verification

The automated test suite currently contains nine tests.

Verified checks:

- Normal Python execution.
- Large input handling.
- Python exception handling.
- Execution timeout.
- Output size restriction.
- Network isolation.
- Non-root execution.
- Linux capabilities and seccomp.
- Memory, CPU and process limits.
- Read-only filesystem.
- /tmp noexec restriction.
- Memory exhaustion classification.
- Container cleanup.

Latest recorded result: 9/9 tests passed.

## 8. Security Considerations

Docker containers provide isolation but share the host Linux kernel.
Container isolation must not be treated as an absolute guarantee
against all container escape vulnerabilities.

Production deployment should:

- Use a dedicated Vultr VM for sandbox execution.
- Never expose the Docker socket publicly.
- Never mount host directories into execution containers.
- Never expose API keys or application secrets to generated code.
- Keep the public API separate from privileged Docker operations.
- Keep Docker and the host operating system updated.
- Consider stronger isolation technologies such as gVisor
  or microVMs for highly adversarial workloads.

## 9. Conclusion

ProofRun combines AI-generated code execution with Docker-based
resource restrictions, network isolation, non-root execution,
output limits, timeout enforcement and automatic container cleanup.

The sandbox is designed to make execution controlled,
observable and repeatable.

## 10. Threat Model

ProofRun treats AI-generated Python code as untrusted input.

Potential threats include:

| Threat | Protection |
|---|---|
| Host filesystem access | Read-only container filesystem |
| Network communication | Docker network disabled |
| Privilege escalation | Non-root user and no-new-privileges |
| Excessive memory consumption | 128 MB memory limit |
| CPU exhaustion | CPU quota, CPU time limit and execution timeout |
| Process creation attacks | 32-process limit |
| Excessive output | 1 MB output limit |
| Large code submissions | 256 KB input limit |
| Container persistence | Forced cleanup after execution |
| Container escape | Docker isolation and host hardening |

## 11. Trust Boundaries

ProofRun contains the following trust boundaries:

1. Frontend to backend:
   All incoming requests must be validated.

2. Backend to AI provider:
   AI-generated code must be considered untrusted.

3. Backend to sandbox:
   Only controlled execution requests should reach the sandbox.

4. Sandbox to host:
   Generated code must not receive Docker socket access,
   host filesystem mounts or application secrets.

5. Sandbox to user:
   Execution results must be returned through controlled
   application responses.

The host operating system and Docker daemon are part of
the trusted computing base.

## 12. Operational Security Requirements

The following controls must be verified before production deployment:

- Restrict Docker daemon access to trusted backend processes.
- Never expose the Docker socket over a public network.
- Do not mount host directories into execution containers.
- Keep API credentials outside source code and container environments.
- Configure firewall rules and restrict public ports.
- Secure SSH access.
- Use HTTPS for public application traffic.
- Apply authentication and rate limiting to execution endpoints.
- Limit concurrent sandbox executions.
- Monitor host CPU, memory and disk usage.
- Keep Docker and operating system packages updated.
- Verify cleanup of abandoned containers after unexpected failures.

These are deployment requirements, not claims that all
production controls have already been implemented.

### Sandbox Concurrency Control

The sandbox currently uses a bounded semaphore to allow a maximum of two simultaneous executions per Python process.

- Requests wait up to one second for an available execution slot.
- Requests that cannot acquire a slot receive the `busy` status.
- Execution slots are released in a `finally` block, including when execution raises an exception.
- This control is process-local. Multiple backend workers can each create their own limit, multiplying total concurrent executions.
- The current deployment should use one backend worker unless a shared cross-process concurrency limiter is implemented.

The semaphore limits concurrent sandbox requests; it does not replace API rate limiting, host resource monitoring or infrastructure-level capacity controls.


## 13. Known Limitations and Residual Risks

- Docker containers share the host Linux kernel.
- Docker isolation is not an absolute guarantee against
  kernel vulnerabilities or container escapes.
- A process or host crash can prevent normal cleanup.
- Docker daemon access is effectively privileged host access.
- Resource limits do not eliminate all host-level denial-of-service risks.
- The default seccomp profile provides additional syscall restrictions
  but is not a complete security boundary.

For highly adversarial workloads, stronger isolation technologies
such as gVisor or dedicated microVMs should be evaluated.

Production deployment must include host monitoring,
concurrency controls and stale-container recovery.
