"""
Simple explanation
- This file defines a data shape (expected input/output fields).
- It validates and documents what data is allowed.
- Think of it as a form template for API data.
"""

from pydantic import BaseModel, Field


class DiagnosisStartDTO(BaseModel):
    prompt: str = Field(..., description="User's initial problem description.")
