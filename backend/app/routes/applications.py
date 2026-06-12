from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.essay_agent import EssayAgent, EssayImproveResult
from app.agents.outreach_agent import (
    GenerateOutreachRequest,
    OutreachAgent,
    OutreachGenerateResult,
)
from app.agents.recommendation_agent import (
    GenerateRecommendationRequest,
    RecommendationAgent,
    RecommendationGenerateResult,
)
from app.db.repository import GrantPilotRepository, get_repository
from app.models import Application
from app.services.application_service import ApplicationBundle, build_application_bundle


router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[Application])
def list_applications(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[Application]:
    return repository.list_applications()


@router.post("", response_model=Application, status_code=201)
def create_application(
    payload: Application,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Application:
    return repository.create_record(payload)


@router.get("/{application_id}", response_model=ApplicationBundle)
def get_application(
    application_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> ApplicationBundle:
    try:
        return build_application_bundle(repository, application_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/{application_id}/improve-essay", response_model=EssayImproveResult)
async def improve_application_essay(
    application_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> EssayImproveResult:
    agent = EssayAgent(repository)
    try:
        return await agent.improve_for_application(application_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{application_id}/generate-recommendation", response_model=RecommendationGenerateResult)
async def generate_application_recommendation(
    application_id: str,
    payload: GenerateRecommendationRequest | None = None,
    repository: GrantPilotRepository = Depends(get_repository),
) -> RecommendationGenerateResult:
    agent = RecommendationAgent(repository)
    try:
        return await agent.generate_for_application(
            application_id,
            payload or GenerateRecommendationRequest(),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{application_id}/generate-outreach", response_model=OutreachGenerateResult)
async def generate_application_outreach(
    application_id: str,
    payload: GenerateOutreachRequest | None = None,
    repository: GrantPilotRepository = Depends(get_repository),
) -> OutreachGenerateResult:
    agent = OutreachAgent(repository)
    try:
        return await agent.generate_for_application(
            application_id,
            payload or GenerateOutreachRequest(),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{application_id}", response_model=Application)
def update_application(
    application_id: str,
    payload: Application,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Application:
    try:
        return repository.update_record(
            Application,
            application_id,
            payload.model_dump(mode="json"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(Application, application_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
