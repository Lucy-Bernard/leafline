"""
Simple explanation
- This file defines a data shape (expected input/output fields).
- It validates and documents what data is allowed.
- Think of it as a form template for API data.
"""

from pydantic import BaseModel, Field


class ChatStartDTO(BaseModel):
    """Data Transfer Object for starting a new chat session."""

    content: str = Field(
        ...,
        description="The user's initial message to start the chat.",
    )
