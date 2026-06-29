"""
Simple explanation
- This file defines a data shape (expected input/output fields).
- It validates and documents what data is allowed.
- Think of it as a form template for API data.
"""

from pydantic import BaseModel, Field


class ChatUpdateDTO(BaseModel):
    """Data Transfer Object for updating an existing chat session."""

    content: str = Field(
        ...,
        description="The user's follow-up message in an existing chat.",
    )
