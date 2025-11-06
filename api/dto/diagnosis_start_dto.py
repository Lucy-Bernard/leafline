from pydantic import BaseModel, Field


class DiagnosisStartDTO(BaseModel):
    prompt: str = Field(..., description="User's initial problem description.")
