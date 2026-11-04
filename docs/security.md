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
