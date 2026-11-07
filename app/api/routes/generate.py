from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import GenerateRequest, GenerateResponse
from app.services.ai_service import generate_code

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

        task = db.query(Task).filter(
            Task.id == task.id,
            Task.user_id == current_user.id,
        ).first()

        if task:
            task.generation_status = "failed"
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Code generation failed. Please try again.",
        ) from exc
