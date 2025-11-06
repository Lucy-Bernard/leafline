"""
APPLICATION CORE: Chat Service Implementation

This service orchestrates general plant care conversations between users and AI.
Unlike the diagnostic kernel, these chats are simpler conversational exchanges
where users can ask general questions about their plants.

Key Responsibilities:
- Start new chat sessions with plant context
- Continue conversations with full message history
- Manage chat lifecycle and persistence
- Provide plant information to AI for contextual responses

Hexagonal Architecture: This is the APPLICATION CORE (business logic).
It depends only on interfaces (ports), never on concrete implementations:
- Repositories (secondary ports) for data persistence
- Adapters (secondary ports) for AI interactions
- Has zero knowledge of databases, HTTP, or external APIs
"""

import uuid
from datetime import UTC, datetime

from adapter.ai_adapter import IAiAdapter
from domain.enum.message_role import MessageRole
from domain.enum.prompt_type import PromptType
from domain.model.chat_message import ChatMessage
from domain.model.general_chat import GeneralChat
from repository.chat_repository import IChatRepository
from repository.diagnosis_repository import IDiagnosisRepository
from repository.plant_repository import IPlantRepository
from repository.prompt_repository import IPromptRepository
from service.chat_service import IChatService


class ChatService(IChatService):
    """
    Chat service orchestrating general plant care conversations.

    Dependencies (injected via constructor following hexagonal architecture):
    - plant_repository: Fetch plant data for conversation context
    - chat_repository: Persist/retrieve chat sessions and messages
    - diagnosis_repository: Fetch recent diagnosis history for context
    - ai_adapter: Generate AI responses to user questions
    - prompt_repository: Load system prompts for plant care conversations
    """

    def __init__(
        self,
        plant_repository: IPlantRepository,
        chat_repository: IChatRepository,
        diagnosis_repository: IDiagnosisRepository,
        ai_adapter: IAiAdapter,
        prompt_repository: IPromptRepository,
    ) -> None:
        self._plant_repository = plant_repository
        self._chat_repository = chat_repository
        self._diagnosis_repository = diagnosis_repository
        self._ai_adapter = ai_adapter
        self._prompt_repository = prompt_repository

    async def start_chat(
        self,
        plant_id: str,
        initial_message: str,
        user_id: str,
    ) -> GeneralChat:
        """Start a new chat session with initial AI response."""
        # Validate plant exists and belongs to user
        plant = await self._plant_repository.get_by_id(plant_id, user_id)
        if not plant:
            error_message = f"Plant with ID {plant_id} not found or unauthorized"
            raise ValueError(error_message)

        # Create new chat session
        chat_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        chat = GeneralChat(
            id=chat_id,
            plant_id=plant_id,
            messages=[],
            created_at=now,
            updated_at=now,
        )

        # Save chat to database
        chat = await self._chat_repository.create_chat(chat)

        # Add user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role=MessageRole.USER,
            content=initial_message,
            created_at=datetime.now(UTC),
        )
        await self._chat_repository.add_message(user_message)

        # Fetch recent diagnoses for context
        recent_diagnoses = await self._diagnosis_repository.get_recent_diagnoses(
            plant_id, limit=3
        )

        # Build diagnosis context
        diagnosis_context = ""
        if recent_diagnoses:
            diagnosis_context = "\n\nRecent Diagnoses:\n"
            for i, diagnosis in enumerate(recent_diagnoses, 1):
                result = diagnosis.diagnosis_context.get("result", {})
                finding = result.get("finding", "N/A")
                recommendation = result.get("recommendation", "N/A")
                diagnosis_context += f"{i}. {finding} - {recommendation}\n"

        # Generate AI response with plant context
        system_prompt = self._prompt_repository.get_prompt(
            PromptType.GENERAL_PLANT_DISCUSSION
        )
        plant_context = (
            f"Plant Name: {plant.name}\n"
            f"Care Instructions: {plant.care_schedule.care_instructions}\n"
            f"Watering Schedule: {plant.care_schedule.watering_schedule}"
            f"{diagnosis_context}"
        )
        user_prompt = f"{plant_context}\n\nUser Question: {initial_message}"

        ai_response_content = self._ai_adapter.get_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Add AI message
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role=MessageRole.AI,
            content=ai_response_content,
            created_at=datetime.now(UTC),
        )
        await self._chat_repository.add_message(ai_message)

        # Retrieve and return updated chat with messages
        updated_chat = await self._chat_repository.get_chat_by_id(chat_id)
        if not updated_chat:
            error_message = f"Chat with ID {chat_id} not found after creation"
            raise ValueError(error_message)

        return updated_chat

    async def continue_chat(
        self,
        chat_id: str,
        user_message: str,
        user_id: str,
    ) -> GeneralChat:
        """Continue an existing chat with full conversation history as context."""
        # Get existing chat
        chat = await self._chat_repository.get_chat_by_id(chat_id)
        if not chat:
            error_message = f"Chat with ID {chat_id} not found"
            raise ValueError(error_message)

        # Verify user owns the plant associated with this chat
        plant = await self._plant_repository.get_by_id(chat.plant_id, user_id)
        if not plant:
            error_message = f"Unauthorized access to chat {chat_id}"
            raise ValueError(error_message)

        # Add user message
        new_user_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role=MessageRole.USER,
            content=user_message,
            created_at=datetime.now(UTC),
        )
        await self._chat_repository.add_message(new_user_message)

        # Build conversation history for context
        conversation_history = "\n".join(
            [f"{msg.role.value}: {msg.content}" for msg in chat.messages],
        )

        # Fetch recent diagnoses for context
        recent_diagnoses = await self._diagnosis_repository.get_recent_diagnoses(
            chat.plant_id, limit=3
        )

        # Build diagnosis context
        diagnosis_context = ""
        if recent_diagnoses:
            diagnosis_context = "\n\nRecent Diagnoses:\n"
            for i, diagnosis in enumerate(recent_diagnoses, 1):
                result = diagnosis.diagnosis_context.get("result", {})
                finding = result.get("finding", "N/A")
                recommendation = result.get("recommendation", "N/A")
                diagnosis_context += f"{i}. {finding} - {recommendation}\n"

        # Generate AI response with plant context and conversation history
        system_prompt = self._prompt_repository.get_prompt(
            PromptType.GENERAL_PLANT_DISCUSSION
        )
        plant_context = (
            f"Plant Name: {plant.name}\n"
            f"Care Instructions: {plant.care_schedule.care_instructions}\n"
            f"Watering Schedule: {plant.care_schedule.watering_schedule}"
            f"{diagnosis_context}"
        )
        user_prompt = (
            f"{plant_context}\n\n"
            f"Conversation History:\n{conversation_history}\n\n"
            f"User Question: {user_message}"
        )

        ai_response_content = self._ai_adapter.get_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Add AI message
        ai_message = ChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            role=MessageRole.AI,
            content=ai_response_content,
            created_at=datetime.now(UTC),
        )
        await self._chat_repository.add_message(ai_message)

        # Retrieve and return updated chat
        updated_chat = await self._chat_repository.get_chat_by_id(chat_id)
        if not updated_chat:
            error_message = f"Chat with ID {chat_id} not found after update"
            raise ValueError(error_message)

        return updated_chat

    async def get_chat(self, chat_id: str, user_id: str) -> GeneralChat:
        """Retrieve a specific chat session by ID."""
        chat = await self._chat_repository.get_chat_by_id(chat_id)
        if not chat:
            error_message = f"Chat with ID {chat_id} not found"
            raise ValueError(error_message)

        # Verify user owns the plant associated with this chat
        plant = await self._plant_repository.get_by_id(chat.plant_id, user_id)
        if not plant:
            error_message = f"Unauthorized access to chat {chat_id}"
            raise ValueError(error_message)

        return chat

    async def get_all_by_plant_id(
        self,
        plant_id: str,
        user_id: str,
    ) -> list[GeneralChat]:
        """Retrieve all chat sessions for a specific plant."""
        # Verify user owns the plant
        plant = await self._plant_repository.get_by_id(plant_id, user_id)
        if not plant:
            error_message = f"Plant with ID {plant_id} not found or unauthorized"
            raise ValueError(error_message)

        return await self._chat_repository.get_all_by_plant_id(plant_id)

    async def delete_chat(self, chat_id: str, user_id: str) -> None:
        """Delete a chat session."""
        # Get chat to verify it exists and user has access
        chat = await self._chat_repository.get_chat_by_id(chat_id)
        if not chat:
            error_message = f"Chat with ID {chat_id} not found"
            raise ValueError(error_message)

        # Verify user owns the plant associated with this chat
        plant = await self._plant_repository.get_by_id(chat.plant_id, user_id)
        if not plant:
            error_message = f"Unauthorized access to chat {chat_id}"
            raise ValueError(error_message)

        # Delete the chat
        deleted = await self._chat_repository.delete_chat(chat_id)
        if not deleted:
            error_message = f"Failed to delete chat with ID {chat_id}"
            raise ValueError(error_message)
