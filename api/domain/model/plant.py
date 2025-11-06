import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .care_schedule import CareSchedule


class Plant(BaseModel):
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
