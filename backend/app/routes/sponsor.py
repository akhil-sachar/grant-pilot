from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.base import AgentResult
from app.agents.sponsor_agent import SponsorAgent
from app.db.repository import GrantPilotRepository, get_repository
from app.db.seed_data import DEFAULT_USER_ID
from app.models.sponsor_scan import SponsorScanStatus
from app.services.scan_state import get_scan_tracker


router = APIRouter(prefix="/sponsor", tags=["sponsor"])


@router.get("/status", response_model=SponsorScanStatus)
def read_scan_status(
    repository: GrantPilotRepository = Depends(get_repository),
) -> SponsorScanStatus:
    tracker = get_scan_tracker()
    runs = sorted(
        repository.list_ingestion_runs(),
        key=lambda run: run.started_at,
        reverse=True,
    )[:20]
    return tracker.snapshot(
        total_opportunities=len(repository.list_opportunities()),
        recent_ingestion_runs=runs,
    )


@router.post("/scan", response_model=AgentResult)
async def trigger_full_scan(
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentResult:
    agent = SponsorAgent(repository)
    return await agent.scan_all(DEFAULT_USER_ID)


@router.post("/scan/{source_name}", response_model=AgentResult)
async def trigger_source_scan(
    source_name: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentResult:
    agent = SponsorAgent(repository)
    result = await agent.scan_source(source_name, DEFAULT_USER_ID)
    if result.status == "failed" and "Unknown source" in result.summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.summary)
    return result
