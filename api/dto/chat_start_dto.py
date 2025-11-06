from pydantic import BaseModel, Field


class ChatStartDTO(BaseModel):
    """Data Transfer Object for starting a new chat session."""

    content: str = Field(
        ...,
        description="The user's initial message to start the chat.",
    )
