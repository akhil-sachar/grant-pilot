from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.services.agent_activity_service import AgentActivityResponse, build_agent_activity


router = APIRouter(prefix="/agent-activity", tags=["agent activity"])


@router.get("", response_model=AgentActivityResponse)
def read_agent_activity(
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentActivityResponse:
    return build_agent_activity(repository)
