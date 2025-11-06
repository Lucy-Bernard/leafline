"""
PRIMARY ADAPTER: Plant Controller

This controller exposes HTTP endpoints for plant CRUD operations.
It handles plant identification, care schedule generation, and plant management.

Key Responsibilities:
- Create new plants (identify from images via Plant.id API)
- Generate AI-powered care schedules
- Retrieve plant details and lists
- Delete plants
- Retrieve diagnosis history for plants

Hexagonal Architecture: This is a PRIMARY ADAPTER that receives external HTTP requests
and translates them into calls to the PlantService (Primary Port / Application Core).

Data Flow:
1. User uploads plant image (base64 encoded)
2. Controller receives DTO and validates JWT
3. Service identifies plant via Plant.id API (Secondary Adapter)
4. Service generates care schedule via AI (Secondary Adapter)
5. Service persists to database via Repository (Secondary Adapter)
6. Controller returns Plant domain model as JSON response
"""

from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from config.container import Container
from config.database import get_db_session
from domain.model.diagnosis_session import DiagnosisSession
from domain.model.plant import Plant
from dto.plant_creation_dto import PlantCreationDTO
from middleware.auth_middleware import get_current_user_id, security
from repository.impl.diagnosis_repository_impl import DiagnosisRepositoryImpl
from repository.impl.plant_repository_impl import PlantRepositoryImpl
from service.diagnosis_service import IDiagnosisService
from service.impl.diagnosis_service_impl import DiagnosisService
from service.impl.plant_service import PlantService
from service.plant_service import IPlantService

router = APIRouter()


def get_plant_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    container: Container = Depends(lambda: Container()),
) -> IPlantService:
    plant_repository = PlantRepositoryImpl(session)
    return PlantService(
        plant_id_adapter=container.plant_id_adapter(),
        prompt_repository=container.prompt_repository(),
        ai_adapter=container.ai_adapter(),
        care_schedule_factory=container.care_schedule_factory(),
        plant_repository=plant_repository,
        storage_adapter=container.storage_adapter(),
    )


@router.post("/")
async def create_plant(
    request: PlantCreationDTO,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    plant_service: Annotated[IPlantService, Depends(get_plant_service)],
) -> Plant:
    """
    Create a new plant by identifying it from an uploaded image.

    Process Flow:
    1. Receives base64-encoded plant image from frontend
    2. Calls Plant.id API to identify the plant species
    3. Validates identification confidence (must be >= 0.7)
    4. Generates personalized care schedule using AI
    5. Uploads image to Supabase storage
    6. Persists plant to database

    Args:
        request: DTO containing base64 image and optional location coordinates
        credentials: JWT bearer token from Supabase authentication
        plant_service: Injected service implementing plant business logic

    Returns:
        Plant: Newly created plant with name, care_schedule, and image_url

    HTTP Status Codes:
        201: Success - plant created
        400: Low identification confidence or invalid image
        500: Internal server error (API failure, database error, etc.)
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await plant_service.create_plant(dto=request, user_id=user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/")
async def get_all_plants(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    plant_service: Annotated[IPlantService, Depends(get_plant_service)],
) -> list[Plant]:
    """
    Retrieve all plants for the authenticated user.

    Returns a list of all plants the user has added to their collection.
    Each plant includes its name, care schedule, and image URL.

    Args:
        credentials: JWT bearer token from Supabase authentication
        plant_service: Injected service implementing plant business logic

    Returns:
        list[Plant]: All plants belonging to the authenticated user

    HTTP Status Codes:
        200: Success - returns plant list (may be empty)
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await plant_service.get_all_plants(user_id=user_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/{plant_id}")
async def get_plant_by_id(
    plant_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    plant_service: Annotated[IPlantService, Depends(get_plant_service)],
) -> Plant:
    """
    Retrieve a specific plant by its ID.

    Returns detailed information for a single plant including its care schedule.
    Only returns the plant if it belongs to the authenticated user.

    Args:
        plant_id: Unique identifier for the plant
        credentials: JWT bearer token from Supabase authentication
        plant_service: Injected service implementing plant business logic

    Returns:
        Plant: The requested plant with all details

    HTTP Status Codes:
        200: Success - plant found
        404: Plant not found or doesn't belong to user
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await plant_service.get_plant_by_id(plant_id=plant_id, user_id=user_id)
    except ValueError as error:
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/{plant_id}")
async def delete_plant(
    plant_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    plant_service: Annotated[IPlantService, Depends(get_plant_service)],
) -> dict[str, str]:
    """
    Delete a plant by its ID.

    Removes the plant from the user's collection. Only allows deletion if the
    plant belongs to the authenticated user.

    Args:
        plant_id: Unique identifier for the plant to delete
        credentials: JWT bearer token from Supabase authentication
        plant_service: Injected service implementing plant business logic

    Returns:
        dict: Status confirmation {"status": "deleted"}

    HTTP Status Codes:
        200: Success - plant deleted
        404: Plant not found or doesn't belong to user
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        await plant_service.delete_plant(plant_id=plant_id, user_id=user_id)
    except ValueError as error:
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    else:
        return {"status": "deleted"}


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


@router.get("/{plant_id}/diagnoses")
async def get_plant_diagnoses(
    plant_id: str,
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(security),
    ],
    diagnosis_service: Annotated[IDiagnosisService, Depends(get_diagnosis_service)],
) -> list[DiagnosisSession]:
    """
    Retrieve all diagnosis sessions for a specific plant.

    Returns the history of all diagnostic conversations for this plant,
    including in-progress and completed diagnoses with full context.

    This allows users to review:
    - Past plant problems and solutions
    - Ongoing diagnoses waiting for user input
    - Complete conversation histories with the AI

    Args:
        plant_id: Unique identifier for the plant
        credentials: JWT bearer token from Supabase authentication
        diagnosis_service: Injected service implementing diagnosis business logic

    Returns:
        list[DiagnosisSession]: All diagnosis sessions for this plant

    HTTP Status Codes:
        200: Success - returns diagnosis list (may be empty)
        404: Plant not found or doesn't belong to user
        400: Invalid request
        500: Internal server error
    """
    try:
        user_id = await get_current_user_id(credentials)
        return await diagnosis_service.get_all_by_plant_id(plant_id, user_id)
    except ValueError as error:
        if "not found" in str(error).lower():
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
