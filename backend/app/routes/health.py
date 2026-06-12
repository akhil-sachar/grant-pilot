from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.db.repository import GrantPilotRepository, get_repository
from app.models import APIModel


class HealthResponse(APIModel):
    status: str
    app_env: str
    demo_mode: bool
    storage_mode: str = "unknown"
    guild_ai_enabled: bool = False
    openui_enabled: bool = False


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(get_settings),
    repository: GrantPilotRepository = Depends(get_repository),
) -> HealthResponse:
    storage = repository.health()
    return HealthResponse(
        status="ok",
        app_env=settings.app_env,
        demo_mode=settings.demo_mode,
        storage_mode=str(storage.get("storage_mode", "unknown")),
        guild_ai_enabled=settings.guild_ai_enabled,
        openui_enabled=settings.openui_enabled,
    )
