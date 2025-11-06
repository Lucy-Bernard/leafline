"""
DEPENDENCY INJECTION CONTAINER

This is the heart of hexagonal architecture dependency management. It wires together all layers
of the application following the dependency inversion principle.

Key Responsibilities:
- Load environment configuration from .env file
- Define all application dependencies and their lifecycles (Singleton vs Factory)
- Wire dependencies following hexagonal architecture principles
- Enable constructor-based dependency injection throughout the application

Hexagonal Architecture Flow:
1. Controllers (Primary Adapters) depend on Service interfaces (Primary Ports)
2. Services (Application Core) depend on Repository/Adapter interfaces (Secondary Ports)
3. Repositories/Adapters (Secondary Adapters) implement those interfaces

This ensures the application core has zero knowledge of external technologies.
All source code dependencies point inward toward the domain.
"""

from collections.abc import AsyncGenerator

from dependency_injector import containers, providers
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from adapter.impl.openrouter_adapter import OpenRouterAdapter
from adapter.impl.plant_id_adapter_impl import PlantIdAdapterImpl
from adapter.impl.sandbox_executor_impl import SandboxExecutorImpl
from adapter.impl.supabase_storage_adapter import SupabaseStorageAdapter
from config.database import get_db_session
from factory.care_schedule_factory import CareScheduleFactory
from repository.impl.chat_repository_impl import ChatRepositoryImpl
from repository.impl.diagnosis_repository_impl import DiagnosisRepositoryImpl
from repository.impl.file_prompt_repository import FilePromptRepository
from repository.impl.plant_repository_impl import PlantRepositoryImpl
from service.impl.chat_service_impl import ChatService
from service.impl.diagnosis_service_impl import DiagnosisService
from service.impl.plant_service import PlantService


async def get_session() -> AsyncGenerator[AsyncSession]:
    async for session in get_db_session():
        yield session


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container implementing hexagonal architecture wiring.

    This container ensures clean separation between layers by injecting dependencies
    through constructors rather than allowing classes to instantiate their own dependencies.
    """

    load_dotenv()

    config = providers.Configuration()
    config.openrouter_api_key.from_env("OPENROUTER_API_KEY")
    config.plant_id_api_key.from_env("PLANT_ID_API_KEY")
    config.supabase_url.from_env("SUPABASE_URL")
    config.supabase_service_role_key.from_env("SUPABASE_SERVICE_ROLE_KEY")
    config.prompt_dir.from_value("domain/prompt")

    care_schedule_factory = providers.Factory(CareScheduleFactory)

    prompt_repository = providers.Singleton(
        FilePromptRepository,
        prompt_dir=config.prompt_dir,
    )

    ai_adapter = providers.Singleton(
        OpenRouterAdapter,
        api_key=config.openrouter_api_key,
    )

    plant_id_adapter = providers.Singleton(
        PlantIdAdapterImpl,
        api_key=config.plant_id_api_key,
    )

    sandbox_executor = providers.Singleton(
        SandboxExecutorImpl,
    )

    storage_adapter = providers.Singleton(
        SupabaseStorageAdapter,
        supabase_url=config.supabase_url,
        supabase_key=config.supabase_service_role_key,
        bucket_name="images",
    )
