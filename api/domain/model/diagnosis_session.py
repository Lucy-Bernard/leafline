"""
Simple explanation
- This file defines a core data model used by the app.
- It describes what information we track and its structure.
- Think of it as a blueprint for important app objects.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from domain.enum.diagnosis_status import DiagnosisStatus


class DiagnosisSession(BaseModel):
    """
    Core domain model for a diagnosis session.
    diagnosis_context is a free-form dict because its shape evolves during the
    kernel cycle — the AI adds plant_vitals, state, and result progressively.
    Using dict[str, Any] lets it grow without Pydantic schema changes.
    """
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
