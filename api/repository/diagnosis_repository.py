"""
Simple explanation
- This file handles reading and writing data storage (database/files).
- It keeps storage details separate from business logic.
- Think of it as a data access helper for the app.
"""

from abc import ABC, abstractmethod

from domain.model.diagnosis_session import DiagnosisSession


class IDiagnosisRepository(ABC):
    """
    Secondary Port for diagnosis session persistence.

    The diagnosis_context (a JSON blob) is the key field — it holds the full
    state of each kernel cycle including conversation history, AI hypotheses,
    plant vitals, and the final result. Implementations must persist and return
    it faithfully so the kernel can resume from exactly where it left off.
    """

    @abstractmethod
    async def create_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """Persist a new diagnosis session and return it with database timestamps."""
        pass

    @abstractmethod
    async def get_session_by_id(self, session_id: str) -> DiagnosisSession | None:
        """Retrieve a full diagnosis session by ID, or None if not found."""
        pass

    @abstractmethod
    async def update_session(self, session: DiagnosisSession) -> DiagnosisSession:
        """
        Overwrite an existing session's status and diagnosis_context.
        Called after every kernel cycle to persist the updated conversation and AI state.
        """
        pass

    @abstractmethod
    async def get_all_by_plant_id(self, plant_id: str) -> list[DiagnosisSession]:
        """Return all diagnosis sessions for a plant (both in-progress and completed)."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session only if the user owns the associated plant. Returns True if deleted."""
        pass

    @abstractmethod
    async def get_recent_diagnoses(
        self, plant_id: str, limit: int = 3
    ) -> list[DiagnosisSession]:
        """Return the most recent completed diagnoses for a plant, used as chat context."""
        pass
