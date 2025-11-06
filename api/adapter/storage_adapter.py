from abc import ABC, abstractmethod


class IStorageAdapter(ABC):
    @abstractmethod
    async def upload_image(self, image_data: str, user_id: str, plant_id: str) -> str:
        pass

    @abstractmethod
    async def delete_image(self, image_url: str) -> bool:
        pass
