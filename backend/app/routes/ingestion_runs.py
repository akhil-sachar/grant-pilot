from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import IngestionRun


router = APIRouter(prefix="/ingestion-runs", tags=["ingestion runs"])


@router.get("", response_model=list[IngestionRun])
def list_ingestion_runs(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[IngestionRun]:
    return repository.list_ingestion_runs()


@router.post("", response_model=IngestionRun, status_code=201)
def create_ingestion_run(
    payload: IngestionRun,
    repository: GrantPilotRepository = Depends(get_repository),
) -> IngestionRun:
    return repository.create_record(payload)


@router.get("/{run_id}", response_model=IngestionRun)
def get_ingestion_run(
    run_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> IngestionRun:
    try:
        return repository.get_record(IngestionRun, run_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{run_id}", response_model=IngestionRun)
def update_ingestion_run(
    run_id: str,
    payload: IngestionRun,
    repository: GrantPilotRepository = Depends(get_repository),
) -> IngestionRun:
    try:
        return repository.update_record(IngestionRun, run_id, payload.model_dump(mode="json"))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{run_id}", status_code=204)
def delete_ingestion_run(
    run_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(IngestionRun, run_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

