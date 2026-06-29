"""
Simple explanation
- This file maps Python objects to database tables/rows.
- ORM means object-relational mapper (code-to-database translator).
- It helps save and load records without manual SQL each time.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.orm.base import Base

if TYPE_CHECKING:
    from domain.orm.chat_message_orm import ChatMessageORM
    from domain.orm.plant_orm import PlantORM


class GeneralChatORM(Base):
    """
    Database table for general plant care chat sessions.
    Each chat belongs to one plant and contains many messages (stored in chat_messages).
    Messages are ordered by created_at so they are always returned in chronological order.
    Cascades delete to its messages.
    """
    __tablename__ = "general_chats"
    __table_args__ = {"schema": "private"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("private.plants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    plant: Mapped["PlantORM"] = relationship(back_populates="general_chats")
    messages: Mapped[list["ChatMessageORM"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessageORM.created_at",
    )
