"""
Simple explanation
- This file handles reading and writing data storage (database/files).
- It keeps storage details separate from business logic.
- Think of it as a data access helper for the app.
"""

import abc

from domain.enum.prompt_type import PromptType


class IPromptRepository(abc.ABC):
    """Secondary Port for accessing prompt data."""

    @abc.abstractmethod
    def get_prompt(self, prompt_type: PromptType) -> str:
        """Retrieves a prompt by type.

        Args:
            prompt_type (PromptType): The type of prompt to retrieve.

        Returns:
            str: The prompt content.

        """
        raise NotImplementedError
