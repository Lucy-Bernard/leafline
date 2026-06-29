"""
Simple explanation
- This file connects our app to an outside system or tool.
- It translates between our app format and external API format.
- Think of it as a bridge to third-party services.
"""

from abc import ABC, abstractmethod


class IStorageAdapter(ABC):
    """
    Secondary Port for cloud image storage.

    Implementations handle uploading plant photos and cleaning them up on delete.
    The application core depends on this interface, not on Supabase specifically —
    the storage provider could be swapped (e.g. to S3) without changing any service code.
    """

    @abstractmethod
    async def upload_image(self, image_data: str, user_id: str, plant_id: str) -> str:
        """
        Upload a base64-encoded image and return its public URL.

        Args:
            image_data: Base64 data URL (e.g. "data:image/jpeg;base64,...")
            user_id: Used to namespace the file path in storage.
            plant_id: Used as the filename in storage.

        Returns:
            str: Publicly accessible URL for the uploaded image.
        """
        pass

    @abstractmethod
    async def delete_image(self, image_url: str) -> bool:
        """
        Delete an image by its public URL.

        Args:
            image_url: The public URL returned by upload_image.

        Returns:
            bool: True if deleted successfully.
        """
        pass
