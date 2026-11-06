# ProofRun

### Execute AI-generated code. Safely. Verify everything.

ProofRun is an AI-powered secure code execution agent that
generates Python code from natural-language tasks and executes
it inside isolated Docker containers.

## Core Workflow

1. User submits a natural-language task.
2. AI generates executable Python code.
3. Backend sends the code to the sandbox.
4. Sandbox executes it inside a restricted Docker container.
5. Execution output and errors are returned.
6. Container is removed after execution.

## Technology Stack

- Frontend: HTML, CSS and JavaScript
- Backend: Python and FastAPI
- AI: Vultr Serverless Inference
- Sandbox: Docker
- Database: SQLite (planned)

## Sandbox Security

- Non-root execution
- Network disabled
- Read-only root filesystem
- 128 MB memory limit
- 0.5 CPU limit
- 32 process limit
- Execution timeout
- 1 MB output limit
- 256 KB input limit
- Linux capabilities dropped
- Seccomp protection
- Automatic container cleanup

## Team Responsibilities

- Member 1: Backend and AI integration
- Member 2: Sandbox and security
- Member 3: Frontend

## Current Progress

The Docker sandbox and security controls are implemented.
All 19 automated tests pass.

Implemented:
- Restricted Docker execution environment
- Resource and output limits
- Network and filesystem isolation
- Non-root execution
- Automatic container cleanup after execution
- Stale-container cleanup utility
- Per-process concurrency limit (2 simultaneous executions)
- Security and integration documentation

Pending:
- Backend and AI integration
- Frontend integration
- Database integration
- End-to-end testing
- Vultr deployment and production hardening

## Security Notice

Docker containers share the host Linux kernel. Container
isolation is not an absolute guarantee against all escapes.

## Hackathon

Built for the Vultr Agent Rush Hackathon.
