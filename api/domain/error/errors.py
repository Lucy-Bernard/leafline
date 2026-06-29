"""
Simple explanation
- This file defines custom errors used by the backend.
- It gives clear names to common failure situations.
- Think of it as a shared error dictionary for the app.
"""

class InvalidPlantNameError(ValueError):
    """Custom exception for invalid plant name inputs."""


class StorageUploadError(Exception):
    """Custom exception for storage upload failures."""


class StorageDeleteError(Exception):
    """Custom exception for storage deletion failures."""
