"""
PRIMARY ADAPTER: Chat Controller

This controller exposes HTTP endpoints for general plant care chat functionality.
It handles conversational AI interactions where users can ask questions about
their plants outside of the diagnostic kernel process.

Key Responsibilities:
- Start new chat sessions with initial messages
- Continue existing chats with follow-up messages
- Retrieve chat history for plants
- Manage chat lifecycle (delete)

Hexagonal Architecture: This is a PRIMARY ADAPTER that receives external HTTP requests
and translates them into calls to the ChatService (Primary Port / Application Core).

The Chat Flow:
1. POST /chats?plant_id=xxx - User starts chat, gets initial AI response
2. PUT /chats/{chat_id} - User continues chat with follow-up
3. GET /chats?plant_id=xxx - User retrieves all chats for a plant
4. GET /chats/{chat_id} - User retrieves specific chat
5. DELETE /chats/{chat_id} - User deletes a chat
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config.container import Container
from config.database import get_db_session
from domain.model.general_chat import GeneralChat
from dto.chat_start_dto import ChatStartDTO
from dto.chat_update_dto import ChatUpdateDTO
from middleware.auth_middleware import get_current_user_id, security
from repository.impl.chat_repository_impl import ChatRepositoryImpl
from repository.impl.diagnosis_repository_impl import DiagnosisRepositoryImpl
from repository.impl.plant_repository_impl import PlantRepositoryImpl
from service.chat_service import IChatService
from service.impl.chat_service_impl import ChatService

router = APIRouter()


def get_chat_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    container: Container = Depends(lambda: Container()),
) -> IChatService:
    plant_repository = PlantRepositoryImpl(session)
    chat_repository = ChatRepositoryImpl(session)
    diagnosis_repository = DiagnosisRepositoryImpl(session)
    return ChatService(
        plant_repository=plant_repository,
        chat_repository=chat_repository,
        diagnosis_repository=diagnosis_repository,
        ai_adapter=container.ai_adapter(),
        prompt_repository=container.prompt_repository(),
    )


@router.get("/")
async def get_all_chats(
    plant_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
) -> list[GeneralChat]:
    """
    Retrieve all chat histories for a specific plant.

    Returns all chat sessions associated with the plant, including
    complete message history for each chat.

    Args:
        plant_id: Query parameter - unique identifier for the plant
        credentials: JWT bearer token from Supabase authentication
        chat_service: Injected service implementing chat business logic

    Returns:
        list[GeneralChat]: All chat sessions for the plant

    HTTP Status Codes:
        200: Success - chats retrieved
        404: Plant not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await chat_service.get_all_by_plant_id(plant_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/")
async def start_chat(
    plant_id: str,
    request: ChatStartDTO,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
) -> GeneralChat:
    """
    Start a new chat session with an initial message.

    Creates a new chat session, processes the user's initial message,
    generates an AI response with plant context, and returns the complete
    chat with both messages.

    Args:
        plant_id: Query parameter - unique identifier for the plant the chat is about
        request: DTO containing the user's initial message
        credentials: JWT bearer token from Supabase authentication
        chat_service: Injected service implementing chat business logic

    Returns:
        GeneralChat: New chat session with initial user and AI messages

    HTTP Status Codes:
        201: Success - chat created
        404: Plant not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await chat_service.start_chat(plant_id, request.content, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/{chat_id}")
async def continue_chat(
    chat_id: str,
    request: ChatUpdateDTO,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
) -> GeneralChat:
    """
    Continue an existing chat with a follow-up message.

    Appends the user's message to the conversation history, uses all
    previous messages as context for the AI, and returns the updated
    chat with the new AI response.

    Args:
        chat_id: Path parameter - unique identifier for the chat session to continue
        request: DTO containing the user's follow-up message
        credentials: JWT bearer token from Supabase authentication
        chat_service: Injected service implementing chat business logic

    Returns:
        GeneralChat: Updated chat with new user and AI messages

    HTTP Status Codes:
        200: Success - chat updated
        404: Chat not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await chat_service.continue_chat(chat_id, request.content, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/{chat_id}")
async def get_chat(
    chat_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
) -> GeneralChat:
    """
    Retrieve a specific chat session by ID.

    Returns the complete chat session including all message history.

    Args:
        chat_id: Path parameter - unique identifier for the chat session
        credentials: JWT bearer token from Supabase authentication
        chat_service: Injected service implementing chat business logic

    Returns:
        GeneralChat: Complete chat session with all messages

    HTTP Status Codes:
        200: Success - chat retrieved
        404: Chat not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await chat_service.get_chat(chat_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
) -> dict[str, str]:
    """
    Delete a specific chat session.

    Removes the chat session and all its message history from the database.

    Args:
        chat_id: Path parameter - unique identifier for the chat session to delete
        credentials: JWT bearer token from Supabase authentication
        chat_service: Injected service implementing chat business logic

    Returns:
        dict: Status confirmation {"status": "deleted"}

    HTTP Status Codes:
        200: Success - chat deleted
        404: Chat not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        await chat_service.delete_chat(chat_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    else:
        return {"status": "deleted"}
