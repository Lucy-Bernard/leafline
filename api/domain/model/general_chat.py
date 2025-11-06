from datetime import datetime

from pydantic import BaseModel, Field

from domain.model.chat_message import ChatMessage


class GeneralChat(BaseModel):
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
