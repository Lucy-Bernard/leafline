import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enum.message_role import MessageRole
from domain.orm.base import Base

if TYPE_CHECKING:
    from domain.orm.general_chat_orm import GeneralChatORM


class ChatMessageORM(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {"schema": "private"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("private.general_chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    chat: Mapped["GeneralChatORM"] = relationship(back_populates="messages")
