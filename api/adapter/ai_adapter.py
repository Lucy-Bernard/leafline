"""
Simple explanation
- This file connects our app to an outside system or tool.
- It translates between our app format and external API format.
- Think of it as a bridge to third-party services.
"""

import abc


class IAiAdapter(abc.ABC):
    """Secondary Port for AI model completions."""

    @abc.abstractmethod
    def get_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Gets a completion from the AI model.

        Args:
            system_prompt (str): The system-level instruction.
            user_prompt (str): The user's input.

        Returns:
            str: The AI-generated response.

        """
        raise NotImplementedError
