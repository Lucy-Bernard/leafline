"""
PRIMARY PORT: Plant Service Interface

Defines the contract for plant identification and management operations.

Hexagonal Architecture: This is a PRIMARY PORT - an interface defining what the
application core can do with plants. Controllers (primary adapters) depend on
this interface, not on the concrete implementation.

Key Capabilities:
- Create plants by identifying from uploaded images
- Generate AI-powered care schedules
- Manage plant CRUD operations
- Associate plants with authenticated users
"""

import abc

from domain.model.plant import Plant
from dto.plant_creation_dto import PlantCreationDTO


class IPlantService(abc.ABC):
    """
    Primary Port defining plant management capabilities.

    Implementations must orchestrate:
    - Plant identification via external API (Plant.id)
    - AI-generated care schedule creation
    - Image storage in cloud
    - Database persistence
    """

    @abc.abstractmethod
    async def create_plant(self, dto: PlantCreationDTO, user_id: str) -> Plant:
        """
        Create a new plant by identifying it from an uploaded image.

        Process:
        1. Identify plant species from image via Plant.id API
        2. Validate identification confidence
        3. Generate personalized care schedule using AI
        4. Upload image to Supabase storage
        5. Persist plant to database

        Args:
            dto: Contains base64-encoded image and optional location data
            user_id: Authenticated user ID

        Returns:
            Plant: Created plant with name, care_schedule, and image_url

        Raises:
            ValueError: If identification confidence too low or creation fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_plants(self, user_id: str) -> list[Plant]:
        """
        Get all plants for a specific user.

        Args:
            user_id: Authenticated user ID

        Returns:
            list[Plant]: All plants belonging to the user
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_plant_by_id(self, plant_id: str, user_id: str) -> Plant:
        """
        Get a specific plant by ID for a user.

        Args:
            plant_id: Plant ID to retrieve
            user_id: Authenticated user ID

        Returns:
            Plant: The plant if found and belongs to user

        Raises:
            ValueError: If plant not found or doesn't belong to user
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_plant(self, plant_id: str, user_id: str) -> None:
        """
        Delete a specific plant by ID for a user.

        Also deletes the associated image from storage.

        Args:
            plant_id: Plant ID to delete
            user_id: Authenticated user ID

        Raises:
            ValueError: If plant not found or doesn't belong to user
        """
        raise NotImplementedError
