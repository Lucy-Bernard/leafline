"""
APPLICATION ENTRY POINT

This file bootstraps the Plant ID API, a FastAPI application built using hexagonal architecture.

Key Responsibilities:
- Initialize the FastAPI application
- Configure CORS for frontend communication
- Wire dependency injection container for hexagonal architecture
- Register API route controllers (primary adapters)

The application features a Diagnostic Kernel that uses AI to dynamically diagnose plant issues
through an interactive, cyclical process where the AI generates executable Python code to
determine each next step in the diagnosis.

Architecture: This is the main entry point that connects all architectural layers together.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.cors import get_cors_origins
from controller.chat_controller import router as chat_router
from controller.diagnosis_controller import router as diagnosis_router
from controller.plant_controller import router as plant_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

app = FastAPI(
    title="Plant Care API",
    description="Generate care schedules for plants using AI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plant_router, prefix="/api/v1/plants")
app.include_router(chat_router, prefix="/api/v1/chats")
app.include_router(diagnosis_router, prefix="/api/v1/diagnoses")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
