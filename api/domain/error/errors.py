class InvalidPlantNameError(ValueError):
    """Custom exception for invalid plant name inputs."""


class StorageUploadError(Exception):
    """Custom exception for storage upload failures."""


class StorageDeleteError(Exception):
    """Custom exception for storage deletion failures."""
