from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class GenerateRequest(BaseModel):
    prompt: str = Field(
        min_length=3,
        max_length=5000,
        description="Describe the Python program you want to generate.",
    )


class GenerateResponse(BaseModel):
    id: str
    prompt: str
    generated_code: str
    model_name: str
    generation_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
