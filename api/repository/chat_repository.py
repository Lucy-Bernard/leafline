"""
Simple explanation
- This file handles reading and writing data storage (database/files).
- It keeps storage details separate from business logic.
- Think of it as a data access helper for the app.
"""

from abc import ABC, abstractmethod

from domain.model.chat_message import ChatMessage
from domain.model.general_chat import GeneralChat


class IChatRepository(ABC):
    """
    Secondary Port for general chat session persistence.

    Unlike diagnosis sessions (which store the full conversation in a JSON blob),
    chat messages are stored as individual rows in the chat_messages table and
    are returned as a list on the GeneralChat model. Implementations must eagerly
    load messages whenever a chat is fetched.
    """

    @abstractmethod
    async def create_chat(self, chat: GeneralChat) -> GeneralChat:
        """Create a new empty chat session and return it."""
        pass

    @abstractmethod
    async def get_chat_by_id(self, chat_id: str) -> GeneralChat | None:
        """Retrieve a chat with all its messages loaded, or None if not found."""
        pass

    @abstractmethod
    async def add_message(self, message: ChatMessage) -> ChatMessage:
        """Append a single message (user or AI) to an existing chat session."""
        pass

    @abstractmethod
    async def get_all_by_plant_id(self, plant_id: str) -> list[GeneralChat]:
        """Return all chats for a plant with messages loaded."""
        pass

    @abstractmethod
    async def get_latest_by_plant_id(self, plant_id: str) -> GeneralChat | None:
        """Return the most recently updated chat for a plant, or None."""
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all its messages. Returns True if deleted."""
        pass
