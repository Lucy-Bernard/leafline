"""
CORS CONFIGURATION

Configures Cross-Origin Resource Sharing (CORS) to allow the Next.js frontend to
communicate with this FastAPI backend.

Key Responsibilities:
- Determine allowed origins based on environment (local, dev, prod)
- Prevent unauthorized cross-origin requests in production
- Allow local development from localhost:3000

This is a security measure that protects the API from unauthorized web applications
while enabling the legitimate frontend to make requests.
"""

import os


def get_cors_origins() -> list[str]:
    """
    Return allowed CORS origins based on the current environment.

    Returns:
        list[str]: List of allowed origin URLs that can make requests to this API
    """
    environment = os.getenv("ENVIRONMENT", "local")

    origins_map = {
        "local": ["http://localhost:3000"],
        "dev": ["https://dev.yourapp.com"],
        "prod": ["https://purple-potatoes-app-f7d6f74074c7.herokuapp.com"],
    }

    return origins_map.get(environment, ["http://localhost:3000"])
