"""
Simple explanation
- This file maps Python objects to database tables/rows.
- ORM means object-relational mapper (code-to-database translator).
- It helps save and load records without manual SQL each time.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.
    All tables are created in the "private" schema in the Supabase PostgreSQL database,
    which keeps them separate from Supabase's own public schema tables.
    """
    metadata = MetaData(schema="private")
