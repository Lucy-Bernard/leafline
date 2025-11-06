from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from domain.enum.diagnosis_status import DiagnosisStatus


class DiagnosisSession(BaseModel):
    id: str = Field(..., description="Unique identifier for the diagnosis session.")
    plant_id: str = Field(..., description="ID of the plant being diagnosed.")
    status: DiagnosisStatus = Field(..., description="Current status of the diagnosis.")
    diagnosis_context: dict[str, Any] = Field(
        ...,
        description="Complete stateful history including initial prompt, plant data, user inputs, and LLM state.",
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the session was created.",
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the session was last updated.",
    )
