"""
Simple explanation
- This file lists fixed option values used across the app.
- It keeps status/type choices consistent and typo-safe.
- Think of it as an approved list of allowed labels.
"""

from enum import Enum


class MessageRole(str, Enum):
    """
    Identifies who sent a chat message — the human user or the AI.
    Stored as a SQL ENUM in the database and serialised to uppercase strings in JSON.
    Note: diagnosis messages use lowercase "user"/"assistant" strings instead (different convention).
    """
    USER = "USER"
    AI = "AI"
