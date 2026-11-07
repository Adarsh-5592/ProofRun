from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.execution import Execution
from app.models.task import Task
from app.models.user import User
from app.schemas.execution import ExecuteRequest, ExecuteResponse
from sandbox.sandbox import run_code

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
    task = db.query(Task).filter(
        Task.id == request.task_id,
        Task.user_id == current_user.id,
    ).first()

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

    result = await run_in_threadpool(
        run_code,
        task.generated_code,
        request.timeout_seconds,
    )

    execution = Execution(
        task_id=task.id,
        user_id=current_user.id,
        status=result["status"],
        stdout=result["stdout"],
        stderr=result["stderr"],
        exit_code=result["exit_code"],
        timed_out=result["timed_out"],
        output_limited=result["output_limited"],
        oom_killed=result["oom_killed"],
        cleanup_ok=result["cleanup_ok"],
        duration_ms=result["duration_ms"],
        error=result["error"],
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    return execution
