"""
Simple explanation
- This file defines a data shape (expected input/output fields).
- It validates and documents what data is allowed.
- Think of it as a form template for API data.
"""

from typing import Any

from pydantic import BaseModel, Field

from domain.enum.diagnosis_status import DiagnosisStatus


class DiagnosisAskResponse(BaseModel):
    diagnosis_id: str = Field(
        ...,
        description="Unique identifier for the diagnosis session.",
    )
    status: DiagnosisStatus = Field(
        ...,
        description="Current status (PENDING_USER_INPUT).",
    )
    ai_question: str = Field(..., description="The question the AI is asking the user.")


class DiagnosisConcludeResponse(BaseModel):
    diagnosis_id: str = Field(
        ...,
        description="Unique identifier for the diagnosis session.",
    )
    status: DiagnosisStatus = Field(..., description="Current status (COMPLETED).")
    result: dict[str, Any] = Field(
        ...,
        description="Final diagnosis with finding and recommendation.",
    )
