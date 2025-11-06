import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.model.chat_message import ChatMessage
from domain.model.general_chat import GeneralChat
from domain.orm.chat_message_orm import ChatMessageORM
from domain.orm.general_chat_orm import GeneralChatORM
from repository.chat_repository import IChatRepository


class ChatRepositoryImpl(IChatRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_chat(self, chat: GeneralChat) -> GeneralChat:
        chat_orm = GeneralChatORM(
            id=uuid.UUID(chat.id) if chat.id else uuid.uuid4(),
            plant_id=uuid.UUID(chat.plant_id),
        )
        self._session.add(chat_orm)
        await self._session.commit()
        await self._session.refresh(chat_orm, ["messages"])
        return self._to_domain(chat_orm)

    async def get_chat_by_id(self, chat_id: str) -> GeneralChat | None:
        result = await self._session.execute(
            select(GeneralChatORM)
            .options(selectinload(GeneralChatORM.messages))
            .where(GeneralChatORM.id == uuid.UUID(chat_id)),
        )
        chat_orm = result.scalar_one_or_none()
        return self._to_domain(chat_orm) if chat_orm else None

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        message_orm = ChatMessageORM(
            id=uuid.UUID(message.id) if message.id else uuid.uuid4(),
            chat_id=uuid.UUID(message.chat_id),
            role=message.role,
            content=message.content,
        )
        self._session.add(message_orm)
        await self._session.commit()
        await self._session.refresh(message_orm)
        return self._to_domain_message(message_orm)

    async def get_all_by_plant_id(self, plant_id: str) -> list[GeneralChat]:
        result = await self._session.execute(
            select(GeneralChatORM)
            .options(selectinload(GeneralChatORM.messages))
            .where(GeneralChatORM.plant_id == uuid.UUID(plant_id)),
        )
        chat_orms = result.scalars().all()
        return [self._to_domain(chat_orm) for chat_orm in chat_orms]

    async def get_latest_by_plant_id(self, plant_id: str) -> GeneralChat | None:
        result = await self._session.execute(
            select(GeneralChatORM)
            .options(selectinload(GeneralChatORM.messages))
            .where(GeneralChatORM.plant_id == uuid.UUID(plant_id))
            .order_by(GeneralChatORM.updated_at.desc())
            .limit(1),
        )
        chat_orm = result.scalar_one_or_none()
        return self._to_domain(chat_orm) if chat_orm else None

    async def delete_chat(self, chat_id: str) -> bool:
        result = await self._session.execute(
            delete(GeneralChatORM).where(GeneralChatORM.id == uuid.UUID(chat_id)),
        )
        await self._session.commit()
        return result.rowcount > 0

    def _to_domain(self, chat_orm: GeneralChatORM) -> GeneralChat:
        return GeneralChat(
            id=str(chat_orm.id),
            plant_id=str(chat_orm.plant_id),
            messages=[self._to_domain_message(m) for m in chat_orm.messages],
            created_at=chat_orm.created_at,
            updated_at=chat_orm.updated_at,
        )

    def _to_domain_message(self, message_orm: ChatMessageORM) -> ChatMessage:
        return ChatMessage(
            id=str(message_orm.id),
            chat_id=str(message_orm.chat_id),
            role=message_orm.role,
            content=message_orm.content,
            created_at=message_orm.created_at,
        )
