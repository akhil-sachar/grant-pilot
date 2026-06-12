from fastapi import APIRouter, Depends

from app.db.repository import GrantPilotRepository, get_repository
from app.models import AgentActionLog


router = APIRouter(prefix="/agent-actions", tags=["agent actions"])


@router.get("", response_model=list[AgentActionLog])
def list_agent_actions(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[AgentActionLog]:
    return repository.list_agent_action_logs()


@router.post("", response_model=AgentActionLog, status_code=201)
def create_agent_action(
    payload: AgentActionLog,
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentActionLog:
    return repository.create_record(payload)


@router.get("/{action_id}", response_model=AgentActionLog)
def get_agent_action(
    action_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentActionLog:
    return repository.get_record(AgentActionLog, action_id)


@router.put("/{action_id}", response_model=AgentActionLog)
def update_agent_action(
    action_id: str,
    payload: AgentActionLog,
    repository: GrantPilotRepository = Depends(get_repository),
) -> AgentActionLog:
    return repository.update_record(AgentActionLog, action_id, payload.model_dump(mode="json"))


@router.delete("/{action_id}", status_code=204)
def delete_agent_action(
    action_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    repository.delete_record(AgentActionLog, action_id)
