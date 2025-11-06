"""
SECONDARY ADAPTER: Diagnosis Repository Implementation

Handles persistence of diagnosis sessions to PostgreSQL database.

This repository is critical for the Diagnostic Kernel because it:
- Stores the diagnosis_context as JSONB (flexible schema for AI state)
- Persists conversation history between kernel cycles
- Maintains AI's internal state (hypotheses, confidence, etc.)
- Stores final diagnosis results

The diagnosis_context JSONB field contains:
- initial_prompt: User's original problem statement
- conversation_history: All user/AI messages
- state: AI's hypotheses and findings (set via LOG_STATE action)
- plant_vitals: Plant name and care schedule (fetched via GET_PLANT_VITALS action)
- result: Final diagnosis and recommendations (set via CONCLUDE action)

Hexagonal Architecture: This is a SECONDARY ADAPTER implementing the
IDiagnosisRepository port. It translates between:
- DiagnosisSession domain models (Pydantic) used by application core
- DiagnosisSessionORM models (SQLAlchemy) used by PostgreSQL

The application core has zero knowledge of SQLAlchemy or PostgreSQL.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from domain.model.diagnosis_session import DiagnosisSession
from domain.orm.diagnosis_session_orm import DiagnosisSessionORM
from repository.diagnosis_repository import IDiagnosisRepository


class DiagnosisRepositoryImpl(IDiagnosisRepository):
    """
    PostgreSQL repository for diagnosis sessions using SQLAlchemy.

    Key Feature: Stores diagnosis_context as JSONB for flexible AI state management.
    PostgreSQL's JSONB type allows efficient querying and indexing of JSON data.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session injected by dependency container
        """
        self._session = session

    async def create_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """
        Create a new diagnosis session in the database.

        Persists the initial diagnosis_context with minimal information:
        - initial_prompt
        - conversation_history with first user message
        - empty state dict (AI will populate)
        - plant_vitals as None (kernel will fetch)

        Args:
            session: Domain model containing diagnosis data

        Returns:
            DiagnosisSession: Persisted session with database-generated timestamps
        """
        session_orm = DiagnosisSessionORM(
            id=uuid.UUID(session.id) if session.id else uuid.uuid4(),
            plant_id=uuid.UUID(session.plant_id),
            status=session.status,
            diagnosis_context=session.diagnosis_context,
        )
        self._session.add(session_orm)
        await self._session.commit()
        await self._session.refresh(session_orm)
        return self._to_domain(session_orm)

    async def get_session_by_id(self, session_id: str) -> DiagnosisSession | None:
        """
        Retrieve a diagnosis session by ID.

        Returns the complete session including full diagnosis_context with
        all conversation history and AI state.

        Args:
            session_id: UUID of the diagnosis session

        Returns:
            DiagnosisSession domain model or None if not found
        """
        result = await self._session.execute(
            select(DiagnosisSessionORM).where(
                DiagnosisSessionORM.id == uuid.UUID(session_id),
            ),
        )
        session_orm = result.scalar_one_or_none()
        return self._to_domain(session_orm) if session_orm else None

    async def update_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """
        Update an existing diagnosis session.

        CRITICAL: This is called after every kernel cycle to persist:
        - Updated conversation_history (new user/AI messages)
        - Updated state (AI's new hypotheses/confidence)
        - Updated plant_vitals (if fetched during cycle)
        - Updated status (PENDING_USER_INPUT → COMPLETED)
        - Final result (if CONCLUDE action executed)

        The diagnosis_context JSONB field is completely replaced with new value.
        PostgreSQL handles this efficiently.

        Args:
            session: Domain model with updated diagnosis_context

        Returns:
            DiagnosisSession: Updated session with new timestamps

        Raises:
            ValueError: If session not found in database
        """
        result = await self._session.execute(
            select(DiagnosisSessionORM).where(
                DiagnosisSessionORM.id == uuid.UUID(session.id),
            ),
        )
        session_orm = result.scalar_one_or_none()
        if not session_orm:
            raise ValueError(f"DiagnosisSession with id {session.id} not found")

        session_orm.status = session.status
        session_orm.diagnosis_context = session.diagnosis_context

        await self._session.commit()
        await self._session.refresh(session_orm)
        return self._to_domain(session_orm)

    async def get_all_by_plant_id(self, plant_id: str) -> list[DiagnosisSession]:
        """
        Retrieve all diagnosis sessions for a specific plant.

        Returns the complete diagnosis history including both:
        - In-progress sessions (PENDING_USER_INPUT)
        - Completed sessions (COMPLETED) with final results

        Each session includes full diagnosis_context with all conversation history.

        Args:
            plant_id: UUID of the plant

        Returns:
            list[DiagnosisSession]: All sessions for the plant (may be empty)
        """
        result = await self._session.execute(
            select(DiagnosisSessionORM).where(
                DiagnosisSessionORM.plant_id == uuid.UUID(plant_id),
            ),
        )
        session_orms = result.scalars().all()
        return [self._to_domain(session_orm) for session_orm in session_orms]

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """
        Delete a diagnosis session with authorization check.

        Joins to plant table to verify the plant belongs to the user before deletion.
        This prevents users from deleting diagnosis sessions for plants they don't own.

        Args:
            session_id: UUID of diagnosis session to delete
            user_id: User ID for authorization

        Returns:
            bool: True if deleted, False if not found or unauthorized
        """
        result = await self._session.execute(
            select(DiagnosisSessionORM)
            .options(joinedload(DiagnosisSessionORM.plant))
            .where(
                DiagnosisSessionORM.id == uuid.UUID(session_id),
            ),
        )
        session_orm = result.unique().scalar_one_or_none()
        if not session_orm:
            return False

        if session_orm.plant.user_id != uuid.UUID(user_id):
            return False

        await self._session.delete(session_orm)
        await self._session.commit()
        return True

    async def get_recent_diagnoses(
        self, plant_id: str, limit: int = 3
    ) -> list[DiagnosisSession]:
        """
        Retrieve most recent completed diagnosis sessions for a plant.

        Returns diagnosis sessions in reverse chronological order (most recent first),
        filtered to only include completed diagnoses with final results.

        Args:
            plant_id: UUID of the plant
            limit: Maximum number of diagnoses to return (default 3)

        Returns:
            list[DiagnosisSession]: Recent completed diagnosis sessions
        """
        from domain.enum.diagnosis_status import DiagnosisStatus

        result = await self._session.execute(
            select(DiagnosisSessionORM)
            .where(
                DiagnosisSessionORM.plant_id == uuid.UUID(plant_id),
                DiagnosisSessionORM.status == DiagnosisStatus.COMPLETED,
            )
            .order_by(DiagnosisSessionORM.updated_at.desc())
            .limit(limit),
        )
        session_orms = result.scalars().all()
        return [self._to_domain(session_orm) for session_orm in session_orms]

    def _to_domain(self, session_orm: DiagnosisSessionORM) -> DiagnosisSession:
        """
        Convert ORM model to domain model.

        CRITICAL TRANSLATION BOUNDARY:
        This method is the boundary between the database layer and application core.
        It translates:
        - UUID (database) → str (domain)
        - DiagnosisSessionORM (SQLAlchemy) → DiagnosisSession (Pydantic)
        - diagnosis_context JSONB (PostgreSQL) → dict (Python)

        The application core never sees SQLAlchemy models - only Pydantic domain models.

        Args:
            session_orm: SQLAlchemy ORM model from database

        Returns:
            DiagnosisSession: Pydantic domain model for application core
        """
        return DiagnosisSession(
            id=str(session_orm.id),
            plant_id=str(session_orm.plant_id),
            status=session_orm.status,
            diagnosis_context=session_orm.diagnosis_context,
            created_at=session_orm.created_at,
            updated_at=session_orm.updated_at,
        )
