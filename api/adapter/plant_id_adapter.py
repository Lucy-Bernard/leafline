"""
Simple explanation
- This file connects our app to an outside system or tool.
- It translates between our app format and external API format.
- Think of it as a bridge to third-party services.
"""

import abc

from dto.plant_creation_dto import PlantCreationDTO


class IPlantIdAdapter(abc.ABC):
    """Secondary Port for plant identification via external API."""

    @abc.abstractmethod
    def identify_plant(self, plant_creation_dto: PlantCreationDTO) -> str:
        """Identifies the plant from images and returns the name.

        Args:
            plant_creation_dto (PlantCreationDTO): The input DTO with images and location.

        Returns:
            str: The identified plant name.

        Raises:
            ValueError: If identification fails or no suggestions.

        """
        raise NotImplementedError
