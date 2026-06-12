from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import RecommendationDraft


router = APIRouter(prefix="/recommendation-drafts", tags=["recommendation drafts"])


@router.get("", response_model=list[RecommendationDraft])
def list_recommendation_drafts(
    application_id: str | None = Query(default=None),
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[RecommendationDraft]:
    return repository.list_recommendation_drafts(application_id)


@router.post("", response_model=RecommendationDraft, status_code=201)
def create_recommendation_draft(
    payload: RecommendationDraft,
    repository: GrantPilotRepository = Depends(get_repository),
) -> RecommendationDraft:
    return repository.create_record(payload)


@router.get("/{draft_id}", response_model=RecommendationDraft)
def get_recommendation_draft(
    draft_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> RecommendationDraft:
    try:
        return repository.get_record(RecommendationDraft, draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{draft_id}", response_model=RecommendationDraft)
def update_recommendation_draft(
    draft_id: str,
    payload: RecommendationDraft,
    repository: GrantPilotRepository = Depends(get_repository),
) -> RecommendationDraft:
    try:
        return repository.update_record(
            RecommendationDraft,
            draft_id,
            payload.model_dump(mode="json"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{draft_id}", status_code=204)
def delete_recommendation_draft(
    draft_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(RecommendationDraft, draft_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

