"""
Simple explanation
- This file marks this folder as a Python package.
- It helps Python know files here belong together.
"""

from domain.enum.diagnosis_status import DiagnosisStatus
from domain.enum.message_role import MessageRole
from domain.enum.prompt_type import PromptType

__all__ = ["DiagnosisStatus", "MessageRole", "PromptType"]
