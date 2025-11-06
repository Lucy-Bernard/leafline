"""
PRIMARY PORT: Diagnosis Service Interface

Defines the contract for the Diagnostic Kernel orchestration service.
This is the heart of the application's AI-driven diagnosis system.

Hexagonal Architecture: This is a PRIMARY PORT - an interface defining what the
application core can do. Controllers (primary adapters) depend on this interface,
not on the concrete implementation.

The Diagnostic Kernel Process:
This service orchestrates a cyclical AI-driven diagnosis where:
1. User provides initial problem statement
2. System sends context to LLM, which generates Python code
3. Code executes in sandbox to determine next action
4. Actions can be:
   - GET_PLANT_VITALS: Fetch plant data, continue cycle
   - LOG_STATE: Save AI hypotheses, continue cycle
   - ASK_USER: Return question to user, pause cycle
   - CONCLUDE: Return final diagnosis, end cycle
5. User provides answer, cycle continues from step 2

This creates a dynamic, stateful conversation driven entirely by AI logic.
"""

import abc

from domain.model.diagnosis_session import DiagnosisSession
from dto.diagnosis_response_dto import DiagnosisAskResponse, DiagnosisConcludeResponse
from dto.diagnosis_start_dto import DiagnosisStartDTO
from dto.diagnosis_update_dto import DiagnosisUpdateDTO


class IDiagnosisService(abc.ABC):
    """
    Primary Port defining the Diagnostic Kernel's capabilities.

    Implementations must orchestrate the cyclical AI diagnosis process,
    managing state through the diagnosis_context and executing AI-generated
    code safely in a sandboxed environment.
    """

    @abc.abstractmethod
    async def start_diagnosis(
        self,
        plant_id: str,
        dto: DiagnosisStartDTO,
        user_id: str,
    ) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
        """
        Initiate a new diagnosis session and run the first kernel cycle.

        Args:
            plant_id: ID of the plant being diagnosed
            dto: Initial problem description from user
            user_id: Authenticated user ID

        Returns:
            DiagnosisAskResponse if AI needs user input
            OR DiagnosisConcludeResponse if AI can diagnose immediately
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def update_diagnosis(
        self,
        diagnosis_id: str,
        dto: DiagnosisUpdateDTO,
        user_id: str,
    ) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
        """
        Continue diagnosis with user's response and run next kernel cycle(s).

        Args:
            diagnosis_id: ID of existing diagnosis session
            dto: User's answer to previous AI question
            user_id: Authenticated user ID

        Returns:
            DiagnosisAskResponse if AI needs more user input
            OR DiagnosisConcludeResponse if AI has reached final diagnosis
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_diagnosis(self, diagnosis_id: str, user_id: str) -> DiagnosisSession:
        """
        Retrieve a diagnosis session with complete context and history.

        Args:
            diagnosis_id: ID of diagnosis session
            user_id: Authenticated user ID

        Returns:
            DiagnosisSession with full conversation and AI state
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_diagnosis(self, diagnosis_id: str, user_id: str) -> None:
        """
        Delete a diagnosis session.

        Args:
            diagnosis_id: ID of diagnosis session to delete
            user_id: Authenticated user ID
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all_by_plant_id(
        self,
        plant_id: str,
        user_id: str,
    ) -> list[DiagnosisSession]:
        """
        Retrieve all diagnosis sessions for a specific plant.

        Args:
            plant_id: ID of the plant
            user_id: Authenticated user ID

        Returns:
            List of all diagnosis sessions for the plant
        """
        raise NotImplementedError
