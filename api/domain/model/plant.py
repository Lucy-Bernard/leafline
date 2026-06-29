"""
Simple explanation
- This file defines a core data model used by the app.
- It describes what information we track and its structure.
- Think of it as a blueprint for important app objects.
"""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .care_schedule import CareSchedule


class Plant(BaseModel):
    """
    Core domain model for a plant.
    This is the object the application core works with — it never sees PlantORM.
    The care_schedule is a strongly-typed Pydantic model (not a raw dict) so the
    service layer always has validated, structured access to care instructions.
    """
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the plant.",
    )
    user_id: uuid.UUID = Field(..., description="ID of the user who owns the plant.")
    name: str = Field(..., description="The common name of the plant.")
    care_schedule: CareSchedule = Field(
        ...,
        description="Care schedule details for the plant.",
    )
    image_url: str | None = Field(None, description="URL of the plant image.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the plant was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the plant was last updated.",
    )
