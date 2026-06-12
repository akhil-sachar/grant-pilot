from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import EssayVersion


router = APIRouter(prefix="/essay-versions", tags=["essay versions"])


@router.get("", response_model=list[EssayVersion])
def list_essay_versions(
    application_id: str | None = Query(default=None),
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[EssayVersion]:
    return repository.list_essay_versions(application_id)


@router.post("", response_model=EssayVersion, status_code=201)
def create_essay_version(
    payload: EssayVersion,
    repository: GrantPilotRepository = Depends(get_repository),
) -> EssayVersion:
    return repository.create_record(payload)


@router.get("/{essay_id}", response_model=EssayVersion)
def get_essay_version(
    essay_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> EssayVersion:
    try:
        return repository.get_record(EssayVersion, essay_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{essay_id}", response_model=EssayVersion)
def update_essay_version(
    essay_id: str,
    payload: EssayVersion,
    repository: GrantPilotRepository = Depends(get_repository),
) -> EssayVersion:
    try:
        return repository.update_record(EssayVersion, essay_id, payload.model_dump(mode="json"))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{essay_id}", status_code=204)
def delete_essay_version(
    essay_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(EssayVersion, essay_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

