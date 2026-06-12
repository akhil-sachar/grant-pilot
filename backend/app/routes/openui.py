from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.services.openui_service import OpenUILayout, build_openui_layout


router = APIRouter(prefix="/openui", tags=["openui"])


@router.get("/layout", response_model=OpenUILayout)
def read_openui_layout(
    repository: GrantPilotRepository = Depends(get_repository),
) -> OpenUILayout:
    return build_openui_layout(repository)
