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
