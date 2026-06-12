from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.db.repository import GrantPilotRepository, get_repository
from app.services.demo_orchestrator import DemoRunResult, run_demo_pipeline


router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/run", response_model=DemoRunResult)
async def run_demo(
    repository: GrantPilotRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> DemoRunResult:
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="Demo pipeline is only available when DEMO_MODE=true.")
    return await run_demo_pipeline(repository)


@router.get("/status")
def demo_status(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "demo_mode": settings.demo_mode,
        "demo_auto_run": settings.demo_auto_run,
        "guild_ai_enabled": settings.guild_ai_enabled,
        "openui_enabled": settings.openui_enabled,
    }
