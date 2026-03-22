"""
APPLICATION CORE: Plant Service Implementation

Orchestrates plant identification, care schedule generation, and management.

This service coordinates multiple external services to create a complete plant profile:
- Plant.id API for species identification
- AI (OpenRouter) for personalized care schedule
- Supabase storage for image hosting
- PostgreSQL database for persistence

Hexagonal Architecture: This is APPLICATION CORE (business logic).
It depends only on interfaces (ports), never on concrete implementations:
- plant_id_adapter (secondary port) for species identification
- ai_adapter (secondary port) for AI completions
- storage_adapter (secondary port) for image storage
- plant_repository (secondary port) for database operations
- Has zero knowledge of specific APIs, databases, or storage systems
"""

import logging
import re
import uuid

from adapter.ai_adapter import IAiAdapter
from adapter.plant_id_adapter import IPlantIdAdapter
from adapter.storage_adapter import IStorageAdapter
from domain.enum.prompt_type import PromptType
from domain.error.errors import InvalidPlantNameError, StorageDeleteError
from domain.model.care_schedule import CareSchedule
from domain.model.plant import Plant
from dto.plant_creation_dto import PlantCreationDTO
from factory.care_schedule_factory import CareScheduleFactory
from repository.plant_repository import IPlantRepository
from repository.prompt_repository import IPromptRepository
from service.plant_service import IPlantService


class PlantService(IPlantService):
    """
    Plant Service orchestrating identification and care schedule generation.

    Dependencies (injected via constructor following hexagonal architecture):
    - plant_id_adapter: Identifies plants from images via Plant.id API
    - ai_adapter: Generates care schedules via LLM
    - storage_adapter: Uploads/deletes images to/from Supabase
    - plant_repository: Persists plant data to PostgreSQL
    - prompt_repository: Loads AI prompts from files
    - care_schedule_factory: Creates CareSchedule domain models from AI responses
    """

    def __init__(
        self,
        plant_id_adapter: IPlantIdAdapter,
        prompt_repository: IPromptRepository,
        ai_adapter: IAiAdapter,
        care_schedule_factory: CareScheduleFactory,
        plant_repository: IPlantRepository,
        storage_adapter: IStorageAdapter,
    ) -> None:
        self._plant_id_adapter = plant_id_adapter
        self._prompt_repository = prompt_repository
        self._ai_adapter = ai_adapter
        self._care_schedule_factory = care_schedule_factory
        self._plant_repository = plant_repository
        self._storage_adapter = storage_adapter

    def _validate_plant_name(self, plant_name: str) -> None:
        """
        Validate that the plant name is legitimate (not empty or only symbols).

        Ensures the plant name:
        - Is not empty or whitespace-only
        - Contains at least one letter (not just numbers/symbols)

        Args:
            plant_name: The plant name to validate

        Raises:
            InvalidPlantNameError: If validation fails
        """
        stripped_name = plant_name.strip()
        if not stripped_name:
            error_message = "Input cannot be empty or contain only whitespace."
            raise InvalidPlantNameError(error_message)

        if not re.search(r"[a-zA-Z]", stripped_name):
            error_message = (
                "Input must be a valid plant name, not just numbers or symbols."
            )
            raise InvalidPlantNameError(error_message)

    def _generate_care_schedule(self, plant_name: str) -> CareSchedule:
        """
        Generate a personalized care schedule using AI.

        Process:
        1. Validate plant name
        2. Load care schedule system prompt (instructions for AI)
        3. Call AI with plant name (e.g., "Monstera Deliciosa")
        4. AI returns JSON with watering, sunlight, fertilizing instructions
        5. Factory parses JSON into CareSchedule domain model

        Args:
            plant_name: Name of the plant (from Plant.id identification)

        Returns:
            CareSchedule: Validated domain model with care instructions
        """
        self._validate_plant_name(plant_name)

        system_prompt = self._prompt_repository.get_prompt(PromptType.PLANT_CARE)

        ai_response_str = self._ai_adapter.get_completion(
            system_prompt=system_prompt,
            user_prompt=plant_name,
        )

        return self._care_schedule_factory.create_from_ai_response(
            ai_response_str,
        )

    async def create_plant(self, dto: PlantCreationDTO, user_id: str) -> Plant:
        """
        Create a new plant by identifying it from an uploaded image.

        Complete Process Flow:
        1. Receive base64-encoded plant image from frontend (via DTO)
        2. Call Plant.id API to identify species
        3. Validate identification confidence >= 0.7
        4. Generate personalized care schedule using AI
        5. Generate unique plant ID
        6. Upload image to Supabase storage bucket
        7. Create Plant domain model
        8. Persist to database via repository
        9. Return complete plant with all data

        Args:
            dto: Contains base64 image and optional location coordinates
            user_id: Authenticated user ID

        Returns:
            Plant: Newly created plant with name, care_schedule, and image_url

        Raises:
            ValueError: If identification fails or any step in creation fails
        """
        try:
            # Use Plant.id adapter to identify plant name
            plant_name = self._plant_id_adapter.identify_plant(dto)
            self._validate_plant_name(plant_name)
            care_schedule = self._generate_care_schedule(plant_name)

            plant_id = str(uuid.uuid4())

            image_url = await self._storage_adapter.upload_image(
                image_data=dto.image,
                user_id=user_id,
                plant_id=plant_id,
            )

            plant = Plant(
                id=plant_id,
                user_id=uuid.UUID(user_id),
                name=plant_name,
                care_schedule=care_schedule,
                image_url=image_url,
            )
            await self._plant_repository.create(plant)
        except Exception as error:
            logging.exception("Failed to create plant")
            error_message = "Plant creation failed"
            raise ValueError(error_message) from error
        else:
            return plant

    async def get_all_plants(self, user_id: str) -> list[Plant]:
        """
        Retrieve all plants for a specific user.

        Returns the user's complete plant collection with all data.

        Args:
            user_id: Authenticated user ID

        Returns:
            list[Plant]: All plants belonging to the user (may be empty)

        Raises:
            ValueError: If database query fails
        """
        try:
            return await self._plant_repository.get_all_by_user_id(user_id)
        except Exception as error:
            logging.exception("Failed to get plants for user")
            error_message = "Failed to retrieve plants"
            raise ValueError(error_message) from error

    async def get_plant_by_id(self, plant_id: str, user_id: str) -> Plant:
        """
        Retrieve a specific plant by ID.

        Validates that the plant exists and belongs to the authenticated user.

        Args:
            plant_id: Plant ID to retrieve
            user_id: Authenticated user ID for authorization

        Returns:
            Plant: The plant with all details

        Raises:
            ValueError: If plant not found or doesn't belong to user
        """
        try:
            plant = await self._plant_repository.get_by_id(plant_id, user_id)
            if plant is None:
                error_message = f"Plant with ID {plant_id} not found"
                raise ValueError(error_message)
            return plant
        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to get plant by ID")
            error_message = "Failed to retrieve plant"
            raise ValueError(error_message) from error

    async def delete_plant(self, plant_id: str, user_id: str) -> None:
        """
        Delete a plant and its associated image.

        Process:
        1. Verify plant exists and belongs to user
        2. Delete image from Supabase storage (if exists)
        3. Delete plant from database

        If image deletion fails (e.g., already deleted manually), we continue
        with plant deletion to avoid orphaned database records.

        Args:
            plant_id: Plant ID to delete
            user_id: Authenticated user ID for authorization

        Raises:
            ValueError: If plant not found or doesn't belong to user
        """
        try:
            plant = await self._plant_repository.get_by_id(plant_id, user_id)
            if plant is None:
                error_message = f"Plant with ID {plant_id} not found"
                raise ValueError(error_message)

            if plant.image_url:
                try:
                    await self._storage_adapter.delete_image(plant.image_url)
                except StorageDeleteError:
                    logging.warning(
                        "Failed to delete image for plant %s, continuing with plant deletion",
                        plant_id,
                    )

            deleted = await self._plant_repository.delete(plant_id, user_id)
            if not deleted:
                error_message = f"Plant with ID {plant_id} not found"
                raise ValueError(error_message)
        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to delete plant")
            error_message = "Failed to delete plant"
            raise ValueError(error_message) from error
