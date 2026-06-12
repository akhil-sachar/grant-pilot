from pydantic import Field
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.services.airbyte_service import AirbyteService
from app.services.composio_service import get_composio_service
from app.models import APIModel


class IntegrationConfig(APIModel):
    clickhouse_enabled: bool = False
    airbyte_enabled: bool = False
    composio_enabled: bool = False
    composio_mode: str = "simulated"
    openai_enabled: bool = False
    openai_model: str = "gpt-4o-mini"
    langfuse_enabled: bool = False
    agent_generation_method: str = "auto"
    guild_ai_enabled: bool = False
    openui_enabled: bool = False


class RuntimeConfig(APIModel):
    app_name: str
    app_env: str
    api_prefix: str
    demo_mode: bool
    demo_auto_run: bool = False
    cors_origins: list[str] = Field(default_factory=list)
    integrations: IntegrationConfig


router = APIRouter(prefix="/config", tags=["config"])


@router.get("", response_model=RuntimeConfig)
def read_config(settings: Settings = Depends(get_settings)) -> RuntimeConfig:
    return RuntimeConfig(
        app_name=settings.app_name,
        app_env=settings.app_env,
        api_prefix=settings.api_prefix,
        demo_mode=settings.demo_mode,
        demo_auto_run=settings.demo_auto_run,
        cors_origins=settings.cors_origins,
        integrations=IntegrationConfig(
            clickhouse_enabled=settings.clickhouse_enabled,
            airbyte_enabled=AirbyteService(settings=settings).is_configured,
            composio_enabled=bool(settings.composio_api_key),
            composio_mode=get_composio_service().mode.value,
            openai_enabled=bool(settings.openai_api_key),
            openai_model=settings.openai_model,
            langfuse_enabled=bool(
                settings.langfuse_enabled
                and settings.langfuse_public_key
                and settings.langfuse_secret_key
            ),
            agent_generation_method=settings.agent_generation_method,
            guild_ai_enabled=settings.guild_ai_enabled,
            openui_enabled=settings.openui_enabled,
        ),
    )
