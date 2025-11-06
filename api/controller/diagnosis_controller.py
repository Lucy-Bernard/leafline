"""
PRIMARY ADAPTER: Diagnosis Controller

This controller exposes HTTP endpoints for the Diagnostic Kernel system.
It handles the interactive, AI-driven plant diagnosis process.

Key Responsibilities:
- Start new diagnosis sessions with initial plant problem
- Update diagnosis with user responses (drives the cyclical kernel loop)
- Retrieve diagnosis session details and history
- Delete diagnosis sessions

Hexagonal Architecture: This is a PRIMARY ADAPTER that receives external HTTP requests
and translates them into calls to the DiagnosisService (Primary Port / Application Core).

The Diagnostic Kernel Flow:
1. POST /{plant_id} - User provides initial problem, kernel starts first cycle
2. AI generates code to determine next action
3. If action is ASK_USER, response contains question for user
4. PUT /{diagnosis_id} - User provides answer, kernel runs next cycle(s)
5. Process repeats until AI generates CONCLUDE action with final diagnosis
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config.container import Container
from config.database import get_db_session
from domain.model.diagnosis_session import DiagnosisSession
from dto.diagnosis_response_dto import DiagnosisAskResponse, DiagnosisConcludeResponse
from dto.diagnosis_start_dto import DiagnosisStartDTO
from dto.diagnosis_update_dto import DiagnosisUpdateDTO
from middleware.auth_middleware import get_current_user_id, security
from repository.impl.diagnosis_repository_impl import DiagnosisRepositoryImpl
from repository.impl.plant_repository_impl import PlantRepositoryImpl
from service.diagnosis_service import IDiagnosisService
from service.impl.diagnosis_service_impl import DiagnosisService

router = APIRouter()


def get_diagnosis_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    container: Container = Depends(lambda: Container()),
) -> IDiagnosisService:
    plant_repository = PlantRepositoryImpl(session)
    diagnosis_repository = DiagnosisRepositoryImpl(session)
    return DiagnosisService(
        plant_repository=plant_repository,
        diagnosis_repository=diagnosis_repository,
        ai_adapter=container.ai_adapter(),
        sandbox_executor=container.sandbox_executor(),
        prompt_repository=container.prompt_repository(),
    )


@router.get("/{diagnosis_id}")
async def get_diagnosis_by_id(
    diagnosis_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    diagnosis_service: Annotated[IDiagnosisService, Depends(get_diagnosis_service)],
) -> DiagnosisSession:
    """
    Retrieve a specific diagnosis session by ID.

    Returns the complete diagnosis context including conversation history,
    AI state, and final result if completed.

    Args:
        diagnosis_id: Unique identifier for the diagnosis session
        credentials: JWT bearer token from Supabase authentication
        diagnosis_service: Injected service implementing diagnosis business logic

    Returns:
        DiagnosisSession: Complete diagnosis session with full context

    HTTP Status Codes:
        200: Success - diagnosis session found
        404: Diagnosis not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await diagnosis_service.get_diagnosis(diagnosis_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/{diagnosis_id}")
async def delete_diagnosis(
    diagnosis_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    diagnosis_service: Annotated[IDiagnosisService, Depends(get_diagnosis_service)],
) -> dict[str, str]:
    """
    Delete a diagnosis session.

    Removes the diagnosis session and all its conversation history from the database.

    Args:
        diagnosis_id: Unique identifier for the diagnosis session to delete
        credentials: JWT bearer token from Supabase authentication
        diagnosis_service: Injected service implementing diagnosis business logic

    Returns:
        dict: Status confirmation {"status": "deleted"}

    HTTP Status Codes:
        200: Success - diagnosis deleted
        404: Diagnosis not found or user unauthorized
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        await diagnosis_service.delete_diagnosis(diagnosis_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    else:
        return {"status": "deleted"}


@router.post("/{plant_id}")
async def start_diagnosis(
    plant_id: str,
    request: DiagnosisStartDTO,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    diagnosis_service: Annotated[IDiagnosisService, Depends(get_diagnosis_service)],
) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
    """
    Start a new diagnosis session - INITIATES THE DIAGNOSTIC KERNEL.

    This is the entry point for the cyclical AI-driven diagnosis process:
    1. Creates a new diagnosis session with initial problem statement
    2. Runs the first kernel cycle(s)
    3. AI generates Python code to analyze the problem
    4. Code executes in sandbox to determine next action
    5. Returns either a question for the user (ASK_USER) or final diagnosis (CONCLUDE)

    The kernel may run multiple internal cycles (GET_PLANT_VITALS, LOG_STATE) before
    pausing to ask the user a question.

    Args:
        plant_id: ID of the plant being diagnosed
        request: DTO containing the initial problem description (e.g., "leaves turning yellow")
        credentials: JWT bearer token from Supabase authentication
        diagnosis_service: Injected service that orchestrates the Diagnostic Kernel

    Returns:
        DiagnosisAskResponse: Contains AI-generated question for user
        OR
        DiagnosisConcludeResponse: Contains final diagnosis (rare on first cycle)

    HTTP Status Codes:
        200: Success - kernel cycle completed
        404: Plant not found
        400: Invalid request or kernel execution failed
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await diagnosis_service.start_diagnosis(plant_id, request, user_id)
    except ValueError as error:
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/{diagnosis_id}")
async def update_diagnosis(
    diagnosis_id: str,
    request: DiagnosisUpdateDTO,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    diagnosis_service: Annotated[IDiagnosisService, Depends(get_diagnosis_service)],
) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
    """
    Update diagnosis with user's response - CONTINUES THE DIAGNOSTIC KERNEL CYCLE.

    This endpoint drives the interactive diagnosis conversation:
    1. Receives user's answer to the previous AI question
    2. Appends answer to conversation history in diagnosis_context
    3. Runs next kernel cycle(s)
    4. AI generates new Python code based on updated context
    5. Code executes to determine next action
    6. Returns either another question or final diagnosis

    The kernel will loop through multiple cycles (fetching plant data, logging hypotheses)
    until it needs user input (ASK_USER) or has enough information to conclude (CONCLUDE).

    Args:
        diagnosis_id: ID of the diagnosis session being updated
        request: DTO containing user's message/answer
        credentials: JWT bearer token from Supabase authentication
        diagnosis_service: Injected service that orchestrates the Diagnostic Kernel

    Returns:
        DiagnosisAskResponse: Contains next AI-generated question
        OR
        DiagnosisConcludeResponse: Contains final diagnosis and recommendations

    HTTP Status Codes:
        200: Success - kernel cycle completed
        404: Diagnosis session not found or unauthorized
        400: Cannot update completed/cancelled diagnosis, or kernel execution failed
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await diagnosis_service.update_diagnosis(diagnosis_id, request, user_id)
    except ValueError as error:
        if "not found" in str(error).lower() or "unauthorized" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        if "cannot update" in str(error).lower():
            raise HTTPException(status_code=400, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
