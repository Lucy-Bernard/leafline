"""
Simple explanation
- This file defines a core data model used by the app.
- It describes what information we track and its structure.
- Think of it as a blueprint for important app objects.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from domain.model.chat_message import ChatMessage


class GeneralChat(BaseModel):
    """Core domain model for a general plant care chat session, including all its messages."""
    id: str = Field(..., description="Unique identifier for the chat.")
    plant_id: str = Field(..., description="ID of the plant this chat is about.")
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="List of messages in this chat.",
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the chat was created.",
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the chat was last updated.",
    )
