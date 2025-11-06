"""
SECONDARY ADAPTER: Plant Repository Implementation

Handles persistence of plant data to PostgreSQL database using SQLAlchemy.

This repository stores:
- Plant identification results from Plant.id API
- AI-generated care schedules as JSONB
- Image URLs from Supabase storage
- User associations for authorization

The care_schedule is stored as JSONB to allow flexible schema without migrations.

Hexagonal Architecture: This is a SECONDARY ADAPTER implementing the
IPlantRepository port. It translates between:
- Plant domain models (Pydantic) used by application core
- PlantORM models (SQLAlchemy) used by PostgreSQL

The application core has zero knowledge of SQLAlchemy or PostgreSQL.
"""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.model.care_schedule import CareSchedule
from domain.model.plant import Plant
from domain.orm.plant_orm import PlantORM
from repository.plant_repository import IPlantRepository


class PlantRepositoryImpl(IPlantRepository):
    """
    PostgreSQL repository for plants using SQLAlchemy.

    Key Feature: Stores care_schedule as JSONB for flexible AI-generated data.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session injected by dependency container
        """
        self._session = session

    async def create(self, plant: Plant) -> Plant:
        plant_orm = PlantORM(
            id=uuid.UUID(plant.id) if plant.id else uuid.uuid4(),
            user_id=plant.user_id,
            name=plant.name,
            care_schedule=plant.care_schedule.model_dump(),
            image_url=plant.image_url,
        )
        self._session.add(plant_orm)
        await self._session.commit()
        await self._session.refresh(plant_orm)
        return self._to_domain(plant_orm)

    async def get_by_id(self, plant_id: str, user_id: str) -> Plant | None:
        result = await self._session.execute(
            select(PlantORM).where(
                PlantORM.id == uuid.UUID(plant_id),
                PlantORM.user_id == user_id,
            ),
        )
        plant_orm = result.scalar_one_or_none()
        return self._to_domain(plant_orm) if plant_orm else None

    async def get_all_by_user_id(self, user_id: str) -> list[Plant]:
        result = await self._session.execute(
            select(PlantORM).where(PlantORM.user_id == user_id),
        )
        plant_orms = result.scalars().all()
        return [self._to_domain(plant_orm) for plant_orm in plant_orms]

    async def update(self, plant: Plant) -> Plant:
        result = await self._session.execute(
            select(PlantORM).where(
                PlantORM.id == uuid.UUID(plant.id),
                PlantORM.user_id == plant.user_id,
            ),
        )
        plant_orm = result.scalar_one_or_none()
        if not plant_orm:
            error_message = f"Plant with id {plant.id} not found"
            raise ValueError(error_message)

        plant_orm.name = plant.name
        plant_orm.care_schedule = plant.care_schedule.model_dump()
        plant_orm.image_url = plant.image_url

        await self._session.commit()
        await self._session.refresh(plant_orm)
        return self._to_domain(plant_orm)

    async def delete(self, plant_id: str, user_id: str) -> bool:
        result = await self._session.execute(
            delete(PlantORM).where(
                PlantORM.id == uuid.UUID(plant_id),
                PlantORM.user_id == user_id,
            ),
        )
        await self._session.commit()
        return result.rowcount > 0

    def _to_domain(self, plant_orm: PlantORM) -> Plant:
        """
        Convert ORM model to domain model.

        CRITICAL TRANSLATION BOUNDARY:
        This method is the boundary between the database layer and application core.
        It translates:
        - UUID (database) → str (domain)
        - PlantORM (SQLAlchemy) → Plant (Pydantic)
        - care_schedule JSONB (PostgreSQL) → CareSchedule (Pydantic)

        The care_schedule JSONB is unpacked into a CareSchedule Pydantic model,
        providing validation and type safety for AI-generated data.

        The application core never sees SQLAlchemy models - only Pydantic domain models.

        Args:
            plant_orm: SQLAlchemy ORM model from database

        Returns:
            Plant: Pydantic domain model for application core
        """
        return Plant(
            id=str(plant_orm.id),
            user_id=plant_orm.user_id,
            name=plant_orm.name,
            care_schedule=CareSchedule(**plant_orm.care_schedule),
            image_url=plant_orm.image_url,
            created_at=plant_orm.created_at,
            updated_at=plant_orm.updated_at,
        )
