from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models import APIModel


class HealthResponse(APIModel):
    status: str
    app_env: str
    demo_mode: bool


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_env=settings.app_env,
        demo_mode=settings.demo_mode,
    )

