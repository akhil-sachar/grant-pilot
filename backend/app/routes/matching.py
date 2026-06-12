from fastapi import APIRouter, Depends

from app.agents.base import AgentResult
from app.agents.matching_agent import MatchingAgent
from app.db.repository import GrantPilotRepository, get_repository
from app.db.seed_data import DEFAULT_USER_ID


router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/run", response_model=AgentResult)
async def run_matching(
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentResult:
    agent = MatchingAgent(repository)
    return await agent.match_all(DEFAULT_USER_ID)
