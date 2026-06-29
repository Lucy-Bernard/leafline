"""
Simple explanation
- This file defines a core data model used by the app.
- It describes what information we track and its structure.
- Think of it as a blueprint for important app objects.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from domain.enum.message_role import MessageRole


class ChatMessage(BaseModel):
    """Core domain model for a single message in a chat session (either USER or AI)."""
    id: str = Field(..., description="Unique identifier for the message.")
    chat_id: str = Field(..., description="ID of the chat this message belongs to.")
    role: MessageRole = Field(
        ...,
        description="Role of the message sender (USER or AI).",
    )
    content: str = Field(..., description="Content of the message.")
    created_at: datetime = Field(
        ...,
        description="Timestamp when the message was created.",
    )
