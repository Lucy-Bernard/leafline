import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.orm.base import Base

if TYPE_CHECKING:
    from domain.orm.diagnosis_session_orm import DiagnosisSessionORM
    from domain.orm.general_chat_orm import GeneralChatORM


class PlantORM(Base):
    __tablename__ = "plants"
    __table_args__ = {"schema": "private"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    care_schedule: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    diagnosis_sessions: Mapped[list["DiagnosisSessionORM"]] = relationship(
        back_populates="plant",
        cascade="all, delete-orphan",
    )
    general_chats: Mapped[list["GeneralChatORM"]] = relationship(
        back_populates="plant",
        cascade="all, delete-orphan",
    )
