from pydantic import BaseModel, Field


class ChatUpdateDTO(BaseModel):
    """Data Transfer Object for updating an existing chat session."""

    content: str = Field(
        ...,
        description="The user's follow-up message in an existing chat.",
    )
