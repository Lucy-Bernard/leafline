"""
Simple explanation
- This file defines a data shape (expected input/output fields).
- It validates and documents what data is allowed.
- Think of it as a form template for API data.
"""

from pydantic import BaseModel, Field


class PlantCreationDTO(BaseModel):
    """DTO for plant creation via image identification."""

    image: str = Field(
        ...,
        description="Base64-encoded image (data:image/... format).",
    )
    latitude: float | None = Field(None, description="Latitude of the plant location.")
    longitude: float | None = Field(
        None,
        description="Longitude of the plant location.",
    )
