from pydantic import Field
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.services.airbyte_service import AirbyteService
from app.models import APIModel


class IntegrationConfig(APIModel):
    clickhouse_enabled: bool = False
    airbyte_enabled: bool = False
    composio_enabled: bool = False
    guild_ai_enabled: bool = False
    openui_enabled: bool = False


class RuntimeConfig(APIModel):
    app_name: str
    app_env: str
    api_prefix: str
    demo_mode: bool
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
        cors_origins=settings.cors_origins,
        integrations=IntegrationConfig(
            clickhouse_enabled=settings.clickhouse_enabled,
            airbyte_enabled=AirbyteService(settings=settings).is_configured,
            composio_enabled=bool(settings.composio_api_key),
            guild_ai_enabled=not settings.demo_mode,
            openui_enabled=not settings.demo_mode,
        ),
    )
