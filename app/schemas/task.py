from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=3,
        max_length=5000,
        description="Describe the Python program you want to generate.",
    )


class GenerateResponse(BaseModel):
    id: str
    prompt: str
    generated_code: str | None
    model_name: str | None
    generation_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
