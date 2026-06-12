from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.services.composio_service import ComposioService, ComposioStatus, get_composio_service


router = APIRouter(prefix="/composio", tags=["composio"])


@router.get("/status", response_model=ComposioStatus)
def read_composio_status(
    repository: GrantPilotRepository = Depends(get_repository),
) -> ComposioStatus:
    return get_composio_service(repository).status()
