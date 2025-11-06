"""
APPLICATION CORE: Diagnosis Service Implementation

THIS IS THE DIAGNOSTIC KERNEL - the heart of the AI-driven diagnosis system.

This service orchestrates a revolutionary cyclical process where:
1. AI generates executable Python code based on diagnosis context
2. Code runs in a sandboxed environment to determine next action
3. Actions update the state and may trigger more cycles
4. Process continues until AI decides to ask user a question or conclude

Key Innovation:
Instead of simple question-answer chat, the AI actively directs the conversation
by writing code that executes in real-time. This creates a truly autonomous
diagnostic agent that can gather information, form hypotheses, and make decisions.

Hexagonal Architecture: This is the APPLICATION CORE (business logic).
It depends only on interfaces (ports), never on concrete implementations:
- Repositories (secondary ports) for data persistence
- Adapters (secondary ports) for AI and code execution
- Has zero knowledge of databases, HTTP, or external APIs

The diagnosis_context (stored as JSONB in database) contains:
- initial_prompt: User's problem description
- conversation_history: All user/AI messages
- state: AI's internal hypotheses and findings
- plant_vitals: Plant name and care schedule
- result: Final diagnosis (when completed)
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from adapter.ai_adapter import IAiAdapter
from adapter.sandbox_executor import ISandboxExecutor
from domain.enum.diagnosis_status import DiagnosisStatus
from domain.enum.prompt_type import PromptType
from domain.model.diagnosis_session import DiagnosisSession
from dto.diagnosis_response_dto import DiagnosisAskResponse, DiagnosisConcludeResponse
from dto.diagnosis_start_dto import DiagnosisStartDTO
from dto.diagnosis_update_dto import DiagnosisUpdateDTO
from repository.diagnosis_repository import IDiagnosisRepository
from repository.plant_repository import IPlantRepository
from repository.prompt_repository import IPromptRepository
from service.diagnosis_service import IDiagnosisService


class DiagnosisService(IDiagnosisService):
    """
    DIAGNOSTIC KERNEL - Orchestrates the cyclical AI-driven diagnosis process.

    This service is the core innovation of the application. It manages:
    - Creating diagnosis sessions with initial context
    - Running the kernel cycle loop
    - Executing AI-generated code safely
    - Managing state transitions
    - Persisting conversation history

    Dependencies (injected via constructor following hexagonal architecture):
    - plant_repository: Fetch plant data during diagnosis
    - diagnosis_repository: Persist/retrieve diagnosis sessions
    - ai_adapter: Generate Python code from context
    - sandbox_executor: Execute AI code safely (RestrictedPython)
    - prompt_repository: Load system prompts for the kernel
    """

    def __init__(
        self,
        plant_repository: IPlantRepository,
        diagnosis_repository: IDiagnosisRepository,
        ai_adapter: IAiAdapter,
        sandbox_executor: ISandboxExecutor,
        prompt_repository: IPromptRepository,
    ) -> None:
        self._plant_repository = plant_repository
        self._diagnosis_repository = diagnosis_repository
        self._ai_adapter = ai_adapter
        self._sandbox_executor = sandbox_executor
        self._prompt_repository = prompt_repository

    async def start_diagnosis(
        self,
        plant_id: str,
        dto: DiagnosisStartDTO,
        user_id: str,
    ) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
        """
        Start a new diagnosis session and run the first kernel cycle.

        Process:
        1. Validate that the plant exists and belongs to the user
        2. Create initial diagnosis_context with user's problem statement
        3. Create new diagnosis session in database with PENDING_USER_INPUT status
        4. Run the kernel cycle to generate first AI response

        The diagnosis_context starts with minimal information:
        - initial_prompt: The user's problem (e.g., "leaves are yellow")
        - conversation_history: [user's initial message]
        - state: {} (empty - AI will populate with hypotheses)
        - plant_vitals: None (kernel will fetch this in first cycle)

        Args:
            plant_id: ID of plant being diagnosed
            dto: Contains the initial problem description
            user_id: Authenticated user ID for authorization

        Returns:
            DiagnosisAskResponse with AI's first question
            OR DiagnosisConcludeResponse if AI can diagnose immediately

        Raises:
            ValueError: If plant not found or kernel execution fails
        """
        try:
            plant = await self._plant_repository.get_by_id(plant_id, user_id)
            if plant is None:
                error_message = f"Plant with ID {plant_id} not found"
                raise ValueError(error_message)

            diagnosis_context: dict[str, Any] = {
                "initial_prompt": dto.prompt,
                "conversation_history": [{"role": "user", "message": dto.prompt}],
                "state": {},
                "plant_vitals": None,
            }

            now = datetime.now(UTC)
            session = DiagnosisSession(
                id=str(uuid.uuid4()),
                plant_id=plant_id,
                status=DiagnosisStatus.PENDING_USER_INPUT,
                diagnosis_context=diagnosis_context,
                created_at=now,
                updated_at=now,
            )

            session = await self._diagnosis_repository.create_session(session)

            return await self._run_kernel_cycle(session, user_id)

        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to start diagnosis")
            error_message = "Failed to start diagnosis"
            raise ValueError(error_message) from error

    async def update_diagnosis(
        self,
        diagnosis_id: str,
        dto: DiagnosisUpdateDTO,
        user_id: str,
    ) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
        """
        Continue diagnosis with user's response and run next kernel cycle(s).

        Process:
        1. Retrieve existing diagnosis session from database
        2. Validate user owns the plant and session is still active
        3. Append user's answer to conversation_history
        4. Run kernel cycle with updated context

        The kernel cycle will:
        - Send enriched context (now including user's answer) to AI
        - AI generates new Python code based on all context
        - Code executes to determine next action
        - May loop through multiple internal actions before asking user again

        Args:
            diagnosis_id: ID of existing diagnosis session
            dto: Contains user's message/answer
            user_id: Authenticated user ID for authorization

        Returns:
            DiagnosisAskResponse with next AI question
            OR DiagnosisConcludeResponse with final diagnosis

        Raises:
            ValueError: If session not found, unauthorized, already completed, or kernel fails
        """
        try:
            session = await self._diagnosis_repository.get_session_by_id(diagnosis_id)
            if session is None:
                error_message = f"Diagnosis session with ID {diagnosis_id} not found"
                raise ValueError(error_message)

            plant = await self._plant_repository.get_by_id(session.plant_id, user_id)
            if plant is None:
                error_message = "Unauthorized access to diagnosis session"
                raise ValueError(error_message)

            if session.status != DiagnosisStatus.PENDING_USER_INPUT:
                error_message = "Cannot update a completed or cancelled diagnosis"
                raise ValueError(error_message)

            session.diagnosis_context["conversation_history"].append(
                {"role": "user", "message": dto.message},
            )

            return await self._run_kernel_cycle(session, user_id)

        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to update diagnosis")
            error_message = "Failed to update diagnosis"
            raise ValueError(error_message) from error

    async def get_diagnosis(self, diagnosis_id: str, user_id: str) -> DiagnosisSession:
        """
        Retrieve a diagnosis session with complete context.

        Returns the full diagnosis session including:
        - Initial problem statement
        - Complete conversation history
        - AI's internal state (hypotheses, confidence)
        - Final result (if completed)

        Validates that the user owns the plant before allowing access.

        Args:
            diagnosis_id: ID of diagnosis session
            user_id: Authenticated user ID for authorization

        Returns:
            DiagnosisSession: Complete session with all context

        Raises:
            ValueError: If session not found or user unauthorized
        """
        try:
            session = await self._diagnosis_repository.get_session_by_id(diagnosis_id)
            if session is None:
                error_message = f"Diagnosis session with ID {diagnosis_id} not found"
                raise ValueError(error_message)

            plant = await self._plant_repository.get_by_id(session.plant_id, user_id)
            if plant is None:
                error_message = "Unauthorized access to diagnosis session"
                raise ValueError(error_message)

            return session

        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to get diagnosis")
            error_message = "Failed to retrieve diagnosis"
            raise ValueError(error_message) from error

    async def delete_diagnosis(self, diagnosis_id: str, user_id: str) -> None:
        """
        Delete a diagnosis session.

        Removes the session and all its conversation history from the database.

        Args:
            diagnosis_id: ID of diagnosis session to delete
            user_id: Authenticated user ID for authorization

        Raises:
            ValueError: If session not found or user unauthorized
        """
        try:
            deleted = await self._diagnosis_repository.delete_session(
                diagnosis_id,
                user_id,
            )
            if not deleted:
                error_message = f"Diagnosis session with ID {diagnosis_id} not found or unauthorized"
                raise ValueError(error_message)
        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to delete diagnosis")
            error_message = "Failed to delete diagnosis"
            raise ValueError(error_message) from error

    async def get_all_by_plant_id(
        self,
        plant_id: str,
        user_id: str,
    ) -> list[DiagnosisSession]:
        """
        Retrieve all diagnosis sessions for a specific plant.

        Returns the complete diagnosis history for a plant, including:
        - In-progress diagnoses waiting for user input
        - Completed diagnoses with final results
        - All conversation histories

        Useful for reviewing past plant problems and solutions.

        Args:
            plant_id: ID of the plant
            user_id: Authenticated user ID for authorization

        Returns:
            list[DiagnosisSession]: All diagnosis sessions for the plant

        Raises:
            ValueError: If plant not found or user unauthorized
        """
        try:
            plant = await self._plant_repository.get_by_id(plant_id, user_id)
            if plant is None:
                error_message = f"Plant with ID {plant_id} not found"
                raise ValueError(error_message)

            return await self._diagnosis_repository.get_all_by_plant_id(plant_id)

        except ValueError:
            raise
        except Exception as error:
            logging.exception("Failed to get diagnoses for plant")
            error_message = "Failed to retrieve diagnoses"
            raise ValueError(error_message) from error

    def _fix_common_syntax_errors(self, code: str) -> str:
        """
        Fix common syntax errors in AI-generated Python code.

        AI models sometimes generate syntactically invalid Python, particularly:
        - if/elif/else blocks with only comments (no executable statements)

        Python requires at least one statement in each block. If the AI writes:
            if condition:
                # comment
            else:
                ...

        This is invalid because the if block has no statement. We fix it by adding 'pass'.

        Args:
            code: AI-generated Python code string

        Returns:
            str: Fixed code with 'pass' statements added where needed
        """
        lines = code.split("\n")
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)

            stripped = line.strip()
            if (
                stripped
                and (
                    stripped.startswith("if ")
                    or stripped.startswith("elif ")
                    or stripped == "else:"
                )
                and stripped.endswith(":")
            ):
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_stripped = next_line.strip()

                    if next_stripped.startswith("#"):
                        if i + 2 < len(lines):
                            line_after_comment = lines[i + 2]
                            current_indent = len(next_line) - len(next_line.lstrip())
                            after_indent = len(line_after_comment) - len(
                                line_after_comment.lstrip(),
                            )

                            if (
                                after_indent <= current_indent
                                and line_after_comment.strip()
                            ):
                                fixed_lines.append(next_line)
                                fixed_lines.append(" " * current_indent + "pass")
                                i += 1
                        else:
                            fixed_lines.append(next_line)
                            current_indent = len(next_line) - len(next_line.lstrip())
                            fixed_lines.append(" " * current_indent + "pass")
                            i += 1

            i += 1

        return "\n".join(fixed_lines)

    async def _run_kernel_cycle(
        self,
        session: DiagnosisSession,
        user_id: str,
    ) -> DiagnosisAskResponse | DiagnosisConcludeResponse:
        """
        THE DIAGNOSTIC KERNEL - Core cyclical AI-driven process.

        This is the heart of the innovation. It creates an autonomous AI agent that:
        1. Analyzes current diagnosis context (problem, plant data, conversation, AI state)
        2. Generates Python code defining the next logical step
        3. Executes code safely in RestrictedPython sandbox
        4. Takes action based on code result
        5. Repeats until user input needed or diagnosis complete

        THE CYCLE LOOP:
        ┌─────────────────────────────────────────────────┐
        │ 1. Build prompt from diagnosis_context         │
        │ 2. AI generates Python code                    │
        │ 3. Execute code in sandbox                     │
        │ 4. Extract action from result                  │
        │ 5. Dispatch action:                            │
        │    - GET_PLANT_VITALS → fetch data, continue  │
        │    - LOG_STATE → save hypothesis, continue    │
        │    - ASK_USER → return question, PAUSE        │
        │    - CONCLUDE → return diagnosis, END         │
        └─────────────────────────────────────────────────┘

        Internal actions (GET_PLANT_VITALS, LOG_STATE) update context and loop.
        External actions (ASK_USER, CONCLUDE) return to user and exit loop.

        Example Cycle Sequence:
        Cycle 1: GET_PLANT_VITALS → fetches plant data, continues
        Cycle 2: LOG_STATE → AI saves hypothesis "overwatering", continues
        Cycle 3: ASK_USER → AI asks "How often do you water?", pauses for user
        [User provides answer]
        Cycle 4: LOG_STATE → AI updates confidence, continues
        Cycle 5: CONCLUDE → AI provides final diagnosis, ends

        Safety:
        - Maximum 20 iterations prevents infinite loops
        - Code executes in RestrictedPython sandbox (no file I/O, network, imports)
        - Syntax errors are caught and fixed automatically

        Args:
            session: Diagnosis session with current context
            user_id: For authorization when fetching plant data

        Returns:
            DiagnosisAskResponse: When AI needs user input (ASK_USER action)
            OR DiagnosisConcludeResponse: When AI finishes diagnosis (CONCLUDE action)

        Raises:
            ValueError: If kernel exceeds max iterations or code execution fails
        """
        max_iterations = 20
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            llm_prompt = self._build_kernel_prompt(session.diagnosis_context)

# I think for this part, the response from openrouter (which is a giant code script) is stored as a string into code 
            code = self._ai_adapter.get_completion(
                system_prompt=self._get_kernel_system_prompt(),
                user_prompt=llm_prompt,
            )

            code = self._fix_common_syntax_errors(code)
            logging.info("Executing kernel code:\n%s", code)

            try:
                result = await self._sandbox_executor.execute_code(
                    code=code,
                    params={"diagnosis_context": session.diagnosis_context},
                )
            except Exception as error:
                logging.exception("Failed to execute kernel code")
                error_message = f"Kernel execution failed: {error!s}"
                raise ValueError(error_message) from error

            action = result.get("action")
            payload = result.get("payload")

            if action == "GET_PLANT_VITALS":
                plant = await self._plant_repository.get_by_id(
                    session.plant_id,
                    user_id,
                )
                if plant is None:
                    error_message = "Plant not found during kernel execution"
                    raise ValueError(error_message)
                session.diagnosis_context["plant_vitals"] = {
                    "name": plant.name,
                    "care_schedule": plant.care_schedule.model_dump(),
                }
                continue

            if action == "LOG_STATE":
                if isinstance(payload, dict):
                    session.diagnosis_context["state"].update(payload)
                continue

            if action == "ASK_USER":
                session.status = DiagnosisStatus.PENDING_USER_INPUT
                if not isinstance(payload, dict):
                    error_message = "ASK_USER payload must be a dictionary"
                    raise ValueError(error_message)
                question = payload.get("question", "")
                session.diagnosis_context["conversation_history"].append(
                    {"role": "assistant", "message": question},
                )
                await self._diagnosis_repository.update_session(session)
                return DiagnosisAskResponse(
                    diagnosis_id=session.id,
                    status=session.status,
                    ai_question=question,
                )

            if action == "CONCLUDE":
                session.status = DiagnosisStatus.COMPLETED
                if not isinstance(payload, dict):
                    error_message = "CONCLUDE payload must be a dictionary"
                    raise ValueError(error_message)
                session.diagnosis_context["result"] = payload
                await self._diagnosis_repository.update_session(session)
                return DiagnosisConcludeResponse(
                    diagnosis_id=session.id,
                    status=session.status,
                    result=payload,
                )

            error_message = f"Unknown action: {action}"
            raise ValueError(error_message)

        error_message = "Kernel exceeded maximum iterations"
        raise ValueError(error_message)

    def _build_kernel_prompt(self, diagnosis_context: dict[str, Any]) -> str:
        """
        Build the user prompt sent to AI containing all diagnosis context.

        This prompt provides the AI with complete situational awareness:
        - The initial problem statement
        - Plant vitals (name and care schedule) if already fetched
        - Full conversation history between user and AI
        - The AI's own internal state (hypotheses, confidence levels, etc.)

        The AI uses this context to generate Python code that determines
        what to do next in the diagnosis process.

        Args:
            diagnosis_context: The JSONB context from the diagnosis session

        Returns:
            str: Formatted prompt with all context for the AI
        """
        plant_vitals = diagnosis_context.get("plant_vitals", "Not yet fetched")
        return f"""You are analyzing a plant diagnosis. Here is the current context:

Initial Problem: {diagnosis_context.get("initial_prompt", "N/A")}

Plant Vitals: {json.dumps(plant_vitals, indent=2)}

Conversation History:
{json.dumps(diagnosis_context.get("conversation_history", []), indent=2)}

Current State (your findings so far):
{json.dumps(diagnosis_context.get("state", {}), indent=2)}

Based on this context, generate the next step in the diagnostic process.
"""

    def _get_kernel_system_prompt(self) -> str:
        """
        Get the system prompt that instructs the AI how to behave as the Diagnostic Kernel.

        The system prompt (loaded from domain/prompt/diagnosis_kernel_prompt.txt):
        - Explains the available actions (GET_PLANT_VITALS, LOG_STATE, ASK_USER, CONCLUDE)
        - Defines the expected code structure and result format
        - Sets the tone for diagnostic conversation
        - Provides examples of valid code

        Returns:
            str: System prompt for the Diagnostic Kernel
        """
        return self._prompt_repository.get_prompt(PromptType.DIAGNOSIS_KERNEL)
