from pydantic import BaseModel, Field


class DiagnosisUpdateDTO(BaseModel):
    message: str = Field(..., description="User's response to AI question.")
