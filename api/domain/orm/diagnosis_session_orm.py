"""
Simple explanation
- This file maps Python objects to database tables/rows.
- ORM means object-relational mapper (code-to-database translator).
- It helps save and load records without manual SQL each time.
"""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enum.diagnosis_status import DiagnosisStatus
from domain.orm.base import Base

if TYPE_CHECKING:
    from domain.orm.plant_orm import PlantORM


class DiagnosisSessionORM(Base):
    """
    Database table for diagnosis sessions (one per AI-driven diagnosis conversation).
    diagnosis_context is stored as JSON — it holds the full kernel state including
    conversation history, AI hypotheses, plant vitals, and the final result.
    Cascades to nothing (messages live in the context JSON, not a separate table).
    """
    __tablename__ = "diagnosis_sessions"
    __table_args__ = {"schema": "private"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    plant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("private.plants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[DiagnosisStatus] = mapped_column(
        SQLEnum(DiagnosisStatus),
        nullable=False,
        default=DiagnosisStatus.PENDING_USER_INPUT,
    )
    diagnosis_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    plant: Mapped["PlantORM"] = relationship(back_populates="diagnosis_sessions")
