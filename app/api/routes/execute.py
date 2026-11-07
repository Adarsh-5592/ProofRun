import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.execution import Execution
from app.models.task import Task
from app.models.user import User
from app.schemas.execution import ExecuteRequest, ExecuteResponse
from sandbox.sandbox import run_code


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Code Execution"])


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def execute_task(
    request: ExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify that the task belongs to the authenticated user.
    task = (
        db.query(Task)
        .filter(
            Task.id == request.task_id,
            Task.user_id == current_user.id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.generation_status != "completed" or not task.generated_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task has no successfully generated code",
        )

    # Capture the values before execution.
    task_id = task.id
    user_id = current_user.id
    generated_code = task.generated_code

    # Create the execution record BEFORE starting Docker.
    execution = Execution(
        task_id=task_id,
        user_id=user_id,
        status="running",
        stdout="",
        stderr="",
        exit_code=None,
        timed_out=False,
        output_limited=False,
        oom_killed=False,
        cleanup_ok=True,
        duration_ms=None,
        error=None,
    )

    db.add(execution)

    try:
        db.commit()
        db.refresh(execution)
    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Could not create execution record for task %s",
            task_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create execution record. Code was not executed.",
        ) from exc

    execution_id = execution.id

    # Execute code only after the initial record is safely committed.
    started = time.monotonic()

    try:
        result = await run_in_threadpool(
            run_code,
            generated_code,
            request.timeout_seconds,
        )

        if not isinstance(result, dict):
            raise RuntimeError("Sandbox returned an invalid result")

    except Exception:
        logger.exception(
            "Unexpected sandbox failure for execution %s",
            execution_id,
        )

        result = {
            "status": "sandbox_error",
            "stdout": "",
            "stderr": "",
            "exit_code": None,
            "timed_out": False,
            "output_limited": False,
            "oom_killed": False,
            "cleanup_ok": False,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "error": "Sandbox execution failed unexpectedly.",
        }

    # Update the existing execution record.
    execution.status = result.get("status") or "sandbox_error"
    execution.stdout = result.get("stdout") or ""
    execution.stderr = result.get("stderr") or ""
    execution.exit_code = result.get("exit_code")
    execution.timed_out = bool(result.get("timed_out", False))
    execution.output_limited = bool(result.get("output_limited", False))
    execution.oom_killed = bool(result.get("oom_killed", False))
    execution.cleanup_ok = bool(result.get("cleanup_ok", False))
    execution.duration_ms = result.get("duration_ms")
    execution.error = result.get("error")

    try:
        db.commit()
        db.refresh(execution)

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Could not save result for execution %s",
            execution_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Execution may have completed, but its result could not be "
                "saved. Check execution history before retrying."
            ),
        ) from exc

    return execution
