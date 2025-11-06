"""
SECONDARY PORT: Plant Repository Interface

Defines the contract for plant data persistence operations.

Hexagonal Architecture: This is a SECONDARY PORT - an interface that the
application core uses to interact with the database. The core depends on this
interface, not on the specific database technology (PostgreSQL/SQLAlchemy).

Key Responsibility:
- Abstract all database operations for plants
- Return domain models (Plant), never ORM models
- Handle user-scoped queries for authorization

This allows the application core to remain database-agnostic.
"""

from abc import ABC, abstractmethod

from domain.model.plant import Plant


class IPlantRepository(ABC):
    """
    Secondary Port for plant data persistence.

    Implementations must translate between:
    - Plant domain models (Pydantic) used by application core
    - PlantORM models (SQLAlchemy) used by database
    """

    @abstractmethod
    async def create(self, plant: Plant) -> Plant:
        """
        Persist a new plant to the database.

        Args:
            plant: Plant domain model to persist

        Returns:
            Plant: The persisted plant with database-generated fields
        """
        pass

    @abstractmethod
    async def get_by_id(self, plant_id: str, user_id: str) -> Plant | None:
        """
        Retrieve a plant by ID, scoped to a specific user.

        Args:
            plant_id: Plant ID to retrieve
            user_id: User ID for authorization (ensures plant belongs to user)

        Returns:
            Plant domain model if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all_by_user_id(self, user_id: str) -> list[Plant]:
        """
        Retrieve all plants for a specific user.

        Args:
            user_id: User ID to retrieve plants for

        Returns:
            list[Plant]: All plants belonging to user (may be empty)
        """
        pass

    @abstractmethod
    async def update(self, plant: Plant) -> Plant:
        """
        Update an existing plant in the database.

        Args:
            plant: Plant domain model with updated fields

        Returns:
            Plant: The updated plant

        Raises:
            ValueError: If plant not found
        """
        pass

    @abstractmethod
    async def delete(self, plant_id: str, user_id: str) -> bool:
        """
        Delete a plant from the database.

        Args:
            plant_id: Plant ID to delete
            user_id: User ID for authorization

        Returns:
            bool: True if deleted, False if not found
        """
        pass
