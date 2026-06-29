"""
Simple explanation
- This file lists fixed option values used across the app.
- It keeps status/type choices consistent and typo-safe.
- Think of it as an approved list of allowed labels.
"""

from enum import Enum


class DiagnosisStatus(str, Enum):
    """
    Lifecycle states for a diagnosis session.
    PENDING_USER_INPUT: kernel ran and is waiting for the user to answer the AI's question.
    COMPLETED: kernel finished and the result (finding + recommendation) has been saved.
    CANCELLED: session was abandoned (not currently used by the kernel, reserved for future).
    Inherits str so it serialises to a plain string in JSON responses.
    """
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
