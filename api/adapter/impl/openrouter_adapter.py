import logging
from typing import Any

from openai import OpenAI

from adapter.ai_adapter import IAiAdapter


class OpenRouterAdapter(IAiAdapter):
    def __init__(self, api_key: str):
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def get_completion(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response: Any = self._client.chat.completions.create(
                model="anthropic/claude-3.5-haiku",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return str(response.choices[0].message.content)
        except Exception as error:
            logging.exception("Failed to get completion from OpenRouter")
            raise error
