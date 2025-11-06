import json
import logging
import re

from domain.model.care_schedule import CareSchedule

logger = logging.getLogger(__name__)


class CareScheduleFactory:
    """Factory for creating CareSchedule objects from various sources."""

    def _clean_ai_response(self, response_str: str) -> str:
        """Clean the AI response to extract valid JSON.

        This method handles common AI response formats including:
        - Markdown code blocks (```json ... ```)
        - Leading/trailing whitespace
        - Text before or after JSON
        - Escaped characters that need normalization

        Args:
            response_str (str): The raw response from the AI.

        Returns:
            str: Cleaned JSON string ready for parsing.

        """
        if not response_str or not isinstance(response_str, str):
            error_message = "Response must be a non-empty string."
            raise ValueError(error_message)

        # Remove leading/trailing whitespace
        cleaned = response_str.strip()

        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Strip again after removing code blocks
        cleaned = cleaned.strip()

        # Try to extract JSON object or array from text
        # Look for the first { or [ and the last } or ]
        json_start = -1
        json_end = -1

        # Find the first opening brace/bracket
        for i, char in enumerate(cleaned):
            if char in ("{", "["):
                json_start = i
                break

        # Find the last closing brace/bracket
        for i in range(len(cleaned) - 1, -1, -1):
            if cleaned[i] in ("}", "]"):
                json_end = i + 1
                break

        # Extract JSON if boundaries found
        if json_start != -1 and json_end != -1 and json_start < json_end:
            cleaned = cleaned[json_start:json_end]

        # Remove any control characters except newlines and tabs
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    def create_from_ai_response(self, response_str: str) -> CareSchedule:
        """Parse a JSON string from an AI response into a CareSchedule.

        This method applies robust cleaning to handle various AI response formats
        before attempting to parse the JSON.

        Args:
            response_str (str): The JSON string response from the AI.

        Returns:
            CareSchedule: A populated CareSchedule object.

        Raises:
            ValueError: If the JSON is malformed or validation fails.
            TypeError: If the response type is invalid.

        """
        cleaned_response = ""
        data = None

        try:
            # Clean the response first
            cleaned_response = self._clean_ai_response(response_str)
            logger.debug("Cleaned AI response: %s", cleaned_response)

            # Parse JSON
            data = json.loads(cleaned_response)

            # Validate that we got a dictionary
            if not isinstance(data, dict):
                error_message = f"Expected JSON object, got {type(data).__name__}."
                raise TypeError(error_message)

            # Create and return the CareSchedule using Pydantic validation
            return CareSchedule(**data)

        except json.JSONDecodeError as error:
            logger.exception(
                "Failed to decode JSON from AI response. Cleaned: %s",
                cleaned_response if cleaned_response else response_str,
            )
            error_message = f"AI response is not valid JSON: {error}"
            raise ValueError(error_message) from error
        except ValueError:
            # Re-raise ValueError (including from _clean_ai_response)
            raise
        except TypeError as error:
            logger.exception(
                "Type error during CareSchedule creation from data: %s",
                data if data is not None else "N/A",
            )
            error_message = f"Invalid data type in AI response: {error}"
            raise ValueError(error_message) from error
        except Exception as error:
            logger.exception(
                "An unexpected error occurred during CareSchedule creation.",
            )
            error_message = f"Failed to create CareSchedule from AI response: {error}"
            raise ValueError(error_message) from error
