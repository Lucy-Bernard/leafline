"""
DATABASE CONNECTION MANAGEMENT

Manages the PostgreSQL database connection using SQLAlchemy's async engine.
This module is critical for the repository layer (secondary adapters) to persist data.

Key Responsibilities:
- Create async database engine from Supabase PostgreSQL connection string
- Provide database sessions for dependency injection into repositories
- Initialize database schema on startup
- Manage connection lifecycle (creation and cleanup)

Hexagonal Architecture: This is infrastructure code that supports secondary adapters
(repositories) but is kept separate from business logic. Repositories depend on
AsyncSession, not on this specific SQLAlchemy implementation.
"""

import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

load_dotenv()


def get_database_url() -> str:
    """
    Retrieve database URL from environment variables.

    Returns:
        str: PostgreSQL connection string for Supabase database

    Raises:
        ValueError: If DATABASE_URL environment variable is not set
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        error_message = "DATABASE_URL environment variable is not set"
        raise ValueError(error_message)
    return database_url


engine = create_async_engine(
    get_database_url(),
    echo=False,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Yield database session for dependency injection into repositories.

    This generator function provides a database session that automatically commits
    on success and rolls back on errors. It ensures connections are properly closed.

    Yields:
        AsyncSession: SQLAlchemy async session for database operations
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Initialize database by creating all tables defined in ORM models.

    This creates the 'private' schema and all tables (plants, diagnosis_sessions,
    general_chats, chat_messages) based on the Base metadata.
    """
    from sqlalchemy import text

    from domain.orm.base import Base

    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS private"))
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database engine and release all connections.

    Should be called on application shutdown to ensure clean resource cleanup.
    """
    await engine.dispose()
