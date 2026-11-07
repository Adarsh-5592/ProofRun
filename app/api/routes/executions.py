
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.execution import Execution
from app.models.user import User
from app.schemas.execution import ExecuteResponse

router = APIRouter(tags=["Execution History"])


@router.get("/executions", response_model=list[ExecuteResponse])
def get_execution_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    executions = (
        db.query(Execution)
        .filter(Execution.user_id == current_user.id)
        .order_by(Execution.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return executions
