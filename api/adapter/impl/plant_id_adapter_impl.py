"""
Simple explanation
- This file connects our app to an outside system or tool.
- It translates between our app format and external API format.
- Think of it as a bridge to third-party services.
"""

import logging
from typing import Any

import requests

from adapter.plant_id_adapter import IPlantIdAdapter
from dto.plant_creation_dto import PlantCreationDTO


class PlantIdAdapterImpl(IPlantIdAdapter):
    """Secondary adapter for Plant.id API identification."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://plant.id/api/v3/identification"

    def identify_plant(self, plant_creation_dto: PlantCreationDTO) -> str:
        """Identifies the plant using Plant.id API.

        Args:
            plant_creation_dto (PlantCreationDTO): Input DTO.

        Returns:
            str: Identified plant name.

        Raises:
            ValueError: On API failure or low confidence.

        """
        payload: dict[str, Any] = {
            "images": [plant_creation_dto.image],
        }
        if plant_creation_dto.latitude is not None:
            payload["latitude"] = plant_creation_dto.latitude
        if plant_creation_dto.longitude is not None:
            payload["longitude"] = plant_creation_dto.longitude

        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            if not response.ok:
                logging.error(
                    "Plant.id API returned %s: %s", response.status_code, response.text
                )
            response.raise_for_status()
            data: Any = response.json()

            if data.get("status") != "COMPLETED":
                raise ValueError(
                    "Plant identification API did not complete successfully",
                )

            suggestions = (
                data.get("result", {}).get("classification", {}).get("suggestions", [])
            )
            if not suggestions:
                raise ValueError("No plant suggestions returned from API")

            top_suggestion = suggestions[0]
            probability = top_suggestion.get("probability", 0)
            if probability < 0.5:
                raise ValueError(f"Low confidence in identification: {probability:.2f}")

            return top_suggestion["name"]

        except requests.RequestException as error:
            body = getattr(getattr(error, "response", None), "text", "")
            logging.exception("Failed to call Plant.id API. Response body: %s", body)
            raise ValueError(f"Plant identification API request failed: {body}") from error
        except ValueError:
            raise
        except (KeyError, Exception) as error:
            logging.exception("Invalid response from Plant.id API")
            raise ValueError("Failed to parse plant identification response") from error
