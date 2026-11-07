
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import GenerateRequest, GenerateResponse
from app.services.ai_service import AIServiceError, generate_code

router = APIRouter(tags=["Code Generation"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_task(
    request: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        user_id=current_user.id,
        prompt=request.prompt,
        generation_status="generating",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Preserve the ID before any operation that might expire the ORM object.
    task_id = task.id
    user_id = current_user.id

    try:
        result = await generate_code(request.prompt)

        task.generated_code = result["code"]
        task.model_name = result["model"]
        task.generation_status = "completed"

        db.commit()
        db.refresh(task)

        return task

    except Exception as exc:
        db.rollback()

        # Re-fetch the task using both its ID and owner ID.
        failed_task = (
            db.query(Task)
            .filter(
                Task.id == task_id,
                Task.user_id == user_id,
            )
            .first()
        )

        if failed_task is not None:
            failed_task.generated_code = None
            failed_task.model_name = None
            failed_task.generation_status = "failed"

            try:
                db.commit()
            except Exception:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not save the generation failure status.",
                ) from exc

        if isinstance(exc, AIServiceError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Code generation failed. Please try again.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during code generation.",
        ) from exc
