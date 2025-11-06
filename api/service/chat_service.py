"""
PRIMARY PORT: Chat Service Interface

Defines the contract for general plant care chat functionality.
This service provides conversational AI capabilities for users to ask
questions about their plants outside of the diagnostic kernel.

Hexagonal Architecture: This is a PRIMARY PORT - an interface defining what the
application core can do. Controllers (primary adapters) depend on this interface,
not on the concrete implementation.

Key Responsibilities:
- Start new chat sessions with initial AI response
- Continue existing chats with conversation history as context
- Retrieve chat history for a plant
- Manage chat lifecycle (delete)
"""

import abc

from domain.model.general_chat import GeneralChat


class IChatService(abc.ABC):
    """
    Primary Port defining general plant care chat capabilities.

    Implementations orchestrate AI-powered conversations about plant care,
    maintaining conversation history and context across multiple exchanges.
    """

    @abc.abstractmethod
    async def start_chat(
        self,
        plant_id: str,
        initial_message: str,
        user_id: str,
    ) -> GeneralChat:
        """
        Start a new chat session with the initial user message.

        Creates a new chat session, sends the user's initial message to the AI
        with plant context, and returns the chat with both user and AI messages.

        Args:
            plant_id: ID of the plant the chat is about
            initial_message: The user's first message/question
            user_id: Authenticated user ID

        Returns:
            GeneralChat: New chat session with initial user message and AI response

        Raises:
            ValueError: If plant not found or user unauthorized
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def continue_chat(
        self,
        chat_id: str,
        user_message: str,
        user_id: str,
    ) -> GeneralChat:
        """
        Continue an existing chat with a follow-up message.

        Appends the user's message to the conversation history, sends all
        previous messages as context to the AI, and returns the updated chat.

        Args:
            chat_id: ID of the existing chat session
            user_message: The user's follow-up message
            user_id: Authenticated user ID

        Returns:
            GeneralChat: Updated chat with new user message and AI response

        Raises:
            ValueError: If chat not found or user unauthorized
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_chat(self, chat_id: str, user_id: str) -> GeneralChat:
        """
        Retrieve a specific chat session by ID.

        Args:
            chat_id: ID of the chat session
            user_id: Authenticated user ID

        Returns:
            GeneralChat: Complete chat with all messages

        Raises:
            ValueError: If chat not found or user unauthorized
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_by_plant_id(
        self,
        plant_id: str,
        user_id: str,
    ) -> list[GeneralChat]:
        """
        Retrieve all chat sessions for a specific plant.

        Args:
            plant_id: ID of the plant
            user_id: Authenticated user ID

        Returns:
            List of all chat sessions for the plant

        Raises:
            ValueError: If plant not found or user unauthorized
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_chat(self, chat_id: str, user_id: str) -> None:
        """
        Delete a chat session.

        Args:
            chat_id: ID of the chat session to delete
            user_id: Authenticated user ID

        Raises:
            ValueError: If chat not found or user unauthorized
        """
        raise NotImplementedError
