from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import Opportunity


router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("", response_model=list[Opportunity])
def list_opportunities(
    tag: str | None = Query(default=None),
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[Opportunity]:
    opportunities = repository.list_opportunities()
    if tag is None:
        return opportunities
    return [item for item in opportunities if tag in item.tags]


@router.post("", response_model=Opportunity, status_code=201)
def create_opportunity(
    payload: Opportunity,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Opportunity:
    return repository.create_record(payload)


@router.get("/{opportunity_id}", response_model=Opportunity)
def get_opportunity(
    opportunity_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Opportunity:
    try:
        return repository.get_opportunity(opportunity_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{opportunity_id}", response_model=Opportunity)
def update_opportunity(
    opportunity_id: str,
    payload: Opportunity,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Opportunity:
    try:
        return repository.update_record(
            Opportunity,
            opportunity_id,
            payload.model_dump(mode="json"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{opportunity_id}", status_code=204)
def delete_opportunity(
    opportunity_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(Opportunity, opportunity_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
