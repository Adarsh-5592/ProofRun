from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecuteRequest(BaseModel):
    task_id: str = Field(min_length=36, max_length=36)
    timeout_seconds: int = Field(default=10, ge=1, le=30)


class ExecuteResponse(BaseModel):
    id: str
    task_id: str
    status: str
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    output_limited: bool
    oom_killed: bool
    cleanup_ok: bool
    duration_ms: int | None
    error: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
