from abc import ABC, abstractmethod

from domain.model.diagnosis_session import DiagnosisSession


class IDiagnosisRepository(ABC):
    @abstractmethod
    async def create_session(self, session: DiagnosisSession) -> DiagnosisSession:
        pass

    @abstractmethod
    async def get_session_by_id(self, session_id: str) -> DiagnosisSession | None:
        pass

    @abstractmethod
    async def update_session(self, session: DiagnosisSession) -> DiagnosisSession:
        pass

    @abstractmethod
    async def get_all_by_plant_id(self, plant_id: str) -> list[DiagnosisSession]:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_recent_diagnoses(
        self, plant_id: str, limit: int = 3
    ) -> list[DiagnosisSession]:
        pass
