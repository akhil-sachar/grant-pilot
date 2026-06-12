from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.models import APIModel, IngestionRun


class StorageHealth(APIModel):
    storage_mode: str
    primary: str | None
    primary_available: bool
    fallback_enabled: bool
    last_error: str | None


router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/health", response_model=StorageHealth)
def read_storage_health(
    repository: GrantPilotRepository = Depends(get_repository),
) -> StorageHealth:
    return StorageHealth.model_validate(repository.health())


@router.post("/initialize", response_model=StorageHealth)
def initialize_storage(
    repository: GrantPilotRepository = Depends(get_repository),
) -> StorageHealth:
    repository.initialize()
    return StorageHealth.model_validate(repository.health())


@router.post("/sample-data", response_model=IngestionRun, status_code=201)
def load_sample_data(
    repository: GrantPilotRepository = Depends(get_repository),
) -> IngestionRun:
    return repository.load_sample_data()

