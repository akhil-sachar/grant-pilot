from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.services.dashboard_service import (
    DashboardAnalytics,
    DashboardResponse,
    build_dashboard,
    build_dashboard_analytics,
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def read_dashboard(
    repository: GrantPilotRepository = Depends(get_repository),
) -> DashboardResponse:
    return build_dashboard(repository)


@router.get("/analytics", response_model=DashboardAnalytics)
def read_dashboard_analytics(
    repository: GrantPilotRepository = Depends(get_repository),
) -> DashboardAnalytics:
    return build_dashboard_analytics(repository)
