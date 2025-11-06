from datetime import datetime

from pydantic import BaseModel, Field

from domain.enum.message_role import MessageRole


class ChatMessage(BaseModel):
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
