from pydantic import BaseModel, Field


class CareSchedule(BaseModel):
    """Pydantic model representing the care schedule for a plant."""

    care_instructions: str = Field(
        ...,
        description="Detailed care instructions covering sunlight, soil, and fertilizer.",
    )
    watering_schedule: str = Field(
        ...,
        description="Specific instructions on how often and how much to water the plant.",
    )
