from enum import Enum


class PromptType(str, Enum):
    PLANT_CARE = "plant_care"
    DIAGNOSIS_KERNEL = "diagnosis_kernel"
    GENERAL_PLANT_DISCUSSION = "general_plant_discussion"
