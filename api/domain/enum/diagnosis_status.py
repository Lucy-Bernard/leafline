from enum import Enum


class DiagnosisStatus(str, Enum):
    PENDING_USER_INPUT = "PENDING_USER_INPUT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
