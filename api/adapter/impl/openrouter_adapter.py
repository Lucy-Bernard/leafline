"""
Simple explanation
- This file connects our app to an outside system or tool.
- It translates between our app format and external API format.
- Think of it as a bridge to third-party services.
"""

import logging
from typing import Any

from openai import OpenAI

from adapter.ai_adapter import IAiAdapter


class OpenRouterAdapter(IAiAdapter):
    """
    Secondary adapter for AI completions via OpenRouter.

    OpenRouter is a unified API gateway that routes requests to multiple LLMs.
    This adapter uses Claude 3.5 Haiku as the underlying model, accessed through
    the OpenAI-compatible SDK (OpenRouter mirrors the OpenAI API format).
    """

    def __init__(self, api_key: str):
        # Uses the OpenAI SDK but points at OpenRouter's base URL —
        # this lets us swap models without changing any code.
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def get_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send a system + user prompt to the LLM and return the text response.

        Args:
            system_prompt: Instructions that set the AI's behaviour/role.
            user_prompt: The actual input or question for this request.

        Returns:
            str: The model's text response.

        Raises:
            Exception: Propagates any OpenRouter API error.
        """
        try:
            response: Any = self._client.chat.completions.create(
                model="anthropic/claude-sonnet-4-6",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return str(response.choices[0].message.content)
        except Exception as error:
            logging.exception("Failed to get completion from OpenRouter")
            raise error
