"""
DATABASE SEEDING UTILITY

Provides functions to seed the database with test data for development and testing.
This is useful for quickly setting up a populated database to test the Diagnostic Kernel
and other features without manually creating data through the API.

Key Responsibilities:
- Drop and recreate database schema for clean testing
- Create sample plants with care schedules
- Create sample diagnosis sessions (both in-progress and completed)
- Create sample general chat conversations
- Demonstrate the diagnosis_context structure used by the Diagnostic Kernel

Usage: Run `python config/seed_db.py` to reset and seed the database.
"""

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal, engine
from domain.enum.diagnosis_status import DiagnosisStatus
from domain.enum.message_role import MessageRole
from domain.orm import Base
from domain.orm.chat_message_orm import ChatMessageORM
from domain.orm.diagnosis_session_orm import DiagnosisSessionORM
from domain.orm.general_chat_orm import GeneralChatORM
from domain.orm.plant_orm import PlantORM


async def drop_all_tables() -> None:
    """
    Drop all tables in the private schema for a clean slate.

    This is useful for testing to ensure a fresh database state.
    """
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS private CASCADE"))
        await conn.execute(text("CREATE SCHEMA private"))


async def create_all_tables() -> None:
    """
    Create all database tables based on ORM model definitions.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_test_data(session: AsyncSession) -> None:
    """
    Seed the database with comprehensive test data.

    Creates:
    - 3 sample plants with different users
    - 2 diagnosis sessions (one in-progress, one completed) demonstrating the kernel
    - 2 general chat conversations with message history

    Args:
        session: Database session for inserting test data
    """
    plant1 = PlantORM(
        id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="Monstera Deliciosa",
        care_schedule={
            "watering": {"frequency": "weekly", "amount": "moderate"},
            "sunlight": {"type": "indirect", "hours": 6},
            "fertilizing": {"frequency": "monthly", "type": "liquid"},
        },
        image_url="https://example.com/monstera.jpg",
    )

    plant2 = PlantORM(
        id=uuid.UUID("10000000-0000-0000-0000-000000000002"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="Snake Plant",
        care_schedule={
            "watering": {"frequency": "biweekly", "amount": "low"},
            "sunlight": {"type": "low to bright indirect", "hours": 4},
            "fertilizing": {"frequency": "quarterly", "type": "slow-release"},
        },
        image_url="https://example.com/snake-plant.jpg",
    )

    plant3 = PlantORM(
        id=uuid.UUID("10000000-0000-0000-0000-000000000003"),
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        name="Pothos",
        care_schedule={
            "watering": {"frequency": "weekly", "amount": "moderate"},
            "sunlight": {"type": "low to bright indirect", "hours": 5},
            "fertilizing": {"frequency": "monthly", "type": "balanced"},
        },
    )

    session.add_all([plant1, plant2, plant3])
    await session.flush()

    diagnosis_session1 = DiagnosisSessionORM(
        id=uuid.UUID("20000000-0000-0000-0000-000000000001"),
        plant_id=plant1.id,
        status=DiagnosisStatus.PENDING_USER_INPUT,
        diagnosis_context={
            "initial_prompt": "My monstera has yellow leaves",
            "plant": {
                "name": "Monstera Deliciosa",
                "care_schedule": {
                    "watering": {"frequency": "weekly", "amount": "moderate"},
                    "sunlight": {"type": "indirect", "hours": 6},
                    "fertilizing": {"frequency": "monthly", "type": "liquid"},
                },
            },
            "conversation_history": [
                {
                    "role": "system",
                    "content": "Plant vitals retrieved successfully",
                    "timestamp": "2025-10-01T10:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "I see your Monstera has yellow leaves. To help diagnose the issue, how often have you been watering it?",
                    "timestamp": "2025-10-01T10:00:05Z",
                },
            ],
            "llm_state": {
                "hypotheses": ["overwatering", "nutrient_deficiency"],
                "confidence": 0.65,
                "questions_asked": 1,
            },
        },
    )

    diagnosis_session2 = DiagnosisSessionORM(
        id=uuid.UUID("20000000-0000-0000-0000-000000000002"),
        plant_id=plant2.id,
        status=DiagnosisStatus.COMPLETED,
        diagnosis_context={
            "initial_prompt": "Snake plant looks droopy",
            "plant": {
                "name": "Snake Plant",
                "care_schedule": {
                    "watering": {"frequency": "biweekly", "amount": "low"},
                    "sunlight": {"type": "low to bright indirect", "hours": 4},
                    "fertilizing": {"frequency": "quarterly", "type": "slow-release"},
                },
            },
            "conversation_history": [
                {
                    "role": "system",
                    "content": "Plant vitals retrieved successfully",
                    "timestamp": "2025-09-28T14:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "How often have you been watering your snake plant?",
                    "timestamp": "2025-09-28T14:00:05Z",
                },
                {
                    "role": "user",
                    "content": "I water it once a week",
                    "timestamp": "2025-09-28T14:05:00Z",
                },
                {
                    "role": "assistant",
                    "content": "Does the pot have drainage holes? And what does the soil feel like?",
                    "timestamp": "2025-09-28T14:05:10Z",
                },
                {
                    "role": "user",
                    "content": "It has drainage holes but the soil feels very wet and smells musty",
                    "timestamp": "2025-09-28T14:08:00Z",
                },
            ],
            "llm_state": {
                "hypotheses": ["root_rot"],
                "confidence": 0.95,
                "questions_asked": 2,
            },
            "result": {
                "finding": "Root Rot",
                "recommendation": "Your snake plant is being overwatered. Snake plants need very infrequent watering - only every 2-3 weeks. The musty smell and wet soil confirm root rot. Remove the plant from its pot, trim away any brown/mushy roots, repot in fresh dry soil, and reduce watering frequency immediately.",
            },
        },
    )

    session.add_all([diagnosis_session1, diagnosis_session2])
    await session.flush()

    general_chat1 = GeneralChatORM(
        id=uuid.UUID("40000000-0000-0000-0000-000000000001"),
        plant_id=plant1.id,
    )

    general_chat2 = GeneralChatORM(
        id=uuid.UUID("40000000-0000-0000-0000-000000000002"),
        plant_id=plant3.id,
    )

    session.add_all([general_chat1, general_chat2])
    await session.flush()

    chat_message1 = ChatMessageORM(
        id=uuid.UUID("50000000-0000-0000-0000-000000000001"),
        chat_id=general_chat1.id,
        role=MessageRole.USER,
        content="How do I propagate my monstera?",
    )

    chat_message2 = ChatMessageORM(
        id=uuid.UUID("50000000-0000-0000-0000-000000000002"),
        chat_id=general_chat1.id,
        role=MessageRole.AI,
        content=(
            "To propagate your monstera, you can take stem cuttings with at "
            "least one node..."
        ),
    )

    chat_message3 = ChatMessageORM(
        id=uuid.UUID("50000000-0000-0000-0000-000000000003"),
        chat_id=general_chat1.id,
        role=MessageRole.USER,
        content="Should I propagate in water or soil?",
    )

    chat_message4 = ChatMessageORM(
        id=uuid.UUID("50000000-0000-0000-0000-000000000004"),
        chat_id=general_chat2.id,
        role=MessageRole.USER,
        content="Can pothos grow in low light?",
    )

    chat_message5 = ChatMessageORM(
        id=uuid.UUID("50000000-0000-0000-0000-000000000005"),
        chat_id=general_chat2.id,
        role=MessageRole.AI,
        content=("Yes, pothos is one of the best plants for low light conditions..."),
    )

    session.add_all(
        [
            chat_message1,
            chat_message2,
            chat_message3,
            chat_message4,
            chat_message5,
        ],
    )
    await session.commit()


async def seed_database() -> None:
    """
    Main seeding function that orchestrates the database reset and population.

    Process:
    1. Drop all existing tables (clean slate)
    2. Create fresh tables from ORM definitions
    3. Insert seed test data
    4. Dispose of database engine
    """
    await drop_all_tables()
    await create_all_tables()

    async with AsyncSessionLocal() as session:
        await seed_test_data(session)

    await engine.dispose()


def main() -> None:
    """
    Entry point for running database seeding.

    Execute with: python config/seed_db.py
    """
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
