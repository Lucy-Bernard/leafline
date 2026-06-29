"""
Simple explanation
- This file lists fixed option values used across the app.
- It keeps status/type choices consistent and typo-safe.
- Think of it as an approved list of allowed labels.
"""

from enum import Enum


class PromptType(str, Enum):
    """
    Keys used to load the correct system prompt from the domain/prompt/ directory.
    Each value maps to a .txt file read by FilePromptRepository at runtime.
    PLANT_CARE: prompt injected during plant creation to generate the care schedule.
    DIAGNOSIS_KERNEL: prompt driving the iterative diagnostic kernel cycle (AI-generated Python code).
    GENERAL_PLANT_DISCUSSION: prompt for open-ended plant care chat sessions.
    """
    PLANT_CARE = "plant_care"
    DIAGNOSIS_KERNEL = "diagnosis_kernel"
    GENERAL_PLANT_DISCUSSION = "general_plant_discussion"
