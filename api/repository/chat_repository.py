from abc import ABC, abstractmethod

from domain.model.chat_message import ChatMessage
from domain.model.general_chat import GeneralChat


class IChatRepository(ABC):
    @abstractmethod
    async def create_chat(self, chat: GeneralChat) -> GeneralChat:
        pass

    @abstractmethod
    async def get_chat_by_id(self, chat_id: str) -> GeneralChat | None:
        pass

    @abstractmethod
    async def add_message(self, message: ChatMessage) -> ChatMessage:
        pass

    @abstractmethod
    async def get_all_by_plant_id(self, plant_id: str) -> list[GeneralChat]:
        pass

    @abstractmethod
    async def get_latest_by_plant_id(self, plant_id: str) -> GeneralChat | None:
        pass

    @abstractmethod
    async def delete_chat(self, chat_id: str) -> bool:
        pass
