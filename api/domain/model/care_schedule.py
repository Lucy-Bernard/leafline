"""
Simple explanation
- This file defines a core data model used by the app.
- It describes what information we track and its structure.
- Think of it as a blueprint for important app objects.
"""

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
