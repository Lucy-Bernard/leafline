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
        payload = {
            "images": [plant_creation_dto.image],
            "latitude": plant_creation_dto.latitude,
            "longitude": plant_creation_dto.longitude,
        }
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
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
                raise ValueError(f"Low confidence in identification: {probability}")

            return top_suggestion["name"]

        except requests.RequestException as error:
            logging.exception("Failed to call Plant.id API")
            raise ValueError("Plant identification API request failed") from error
        except (KeyError, ValueError) as error:
            logging.exception("Invalid response from Plant.id API")
            raise ValueError("Failed to parse plant identification response") from error
        except Exception as error:
            logging.exception("Unexpected error during plant identification")
            raise ValueError("Unexpected error in plant identification") from error
