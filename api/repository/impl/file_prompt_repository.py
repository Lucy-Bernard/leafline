import logging
import os

from domain.enum.prompt_type import PromptType
from repository.prompt_repository import IPromptRepository


class FilePromptRepository(IPromptRepository):
    """Secondary adapter to retrieve prompts from text files."""

    PROMPT_FILES = {
        PromptType.PLANT_CARE: "plant_care_prompt.txt",
        PromptType.DIAGNOSIS_KERNEL: "diagnosis_kernel_prompt.txt",
        PromptType.GENERAL_PLANT_DISCUSSION: "general_plant_discussion_prompt.txt",
    }

    def __init__(self, prompt_dir: str) -> None:
        """Initialize the repository with the path to the prompt directory.

        Args:
            prompt_dir (str): The directory containing prompt files.

        """
        self._prompt_dir = prompt_dir

    def get_prompt(self, prompt_type: PromptType) -> str:
        """Read a prompt from file by type.

        Args:
            prompt_type (PromptType): The type of prompt to retrieve.

        Returns:
            str: The content of the prompt file.

        Raises:
            ValueError: If the prompt type is unknown.
            FileNotFoundError: If the prompt file does not exist.

        """
        filename = self.PROMPT_FILES.get(prompt_type)
        if not filename:
            error_message = f"Unknown prompt type: {prompt_type}"
            raise ValueError(error_message)

        file_path = os.path.join(self._prompt_dir, filename)

        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError as error:
            logging.exception(f"Prompt file not found at path: {file_path}")
            raise error
        except Exception as error:
            logging.exception(
                "An unexpected error occurred while reading the prompt file.",
            )
            raise error
