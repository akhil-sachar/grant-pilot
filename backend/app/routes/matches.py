from fastapi import APIRouter, Depends

from fastapi import HTTPException, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import MatchResult


router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchResult])
def list_matches(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[MatchResult]:
    return repository.list_matches()


@router.post("", response_model=MatchResult, status_code=201)
def create_match(
    payload: MatchResult,
    repository: GrantPilotRepository = Depends(get_repository),
) -> MatchResult:
    return repository.create_record(payload)


@router.get("/{match_id}", response_model=MatchResult)
def get_match(
    match_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> MatchResult:
    try:
        return repository.get_record(MatchResult, match_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{match_id}", response_model=MatchResult)
def update_match(
    match_id: str,
    payload: MatchResult,
    repository: GrantPilotRepository = Depends(get_repository),
) -> MatchResult:
    try:
        return repository.update_record(MatchResult, match_id, payload.model_dump(mode="json"))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{match_id}", status_code=204)
def delete_match(
    match_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(MatchResult, match_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
