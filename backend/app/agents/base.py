from typing import ClassVar

from pydantic import Field

from app.models import APIModel, Metadata


class AgentContext(APIModel):
    user_id: str
    application_id: str | None = None
    opportunity_id: str | None = None
    metadata: Metadata = Field(default_factory=dict)


class AgentResult(APIModel):
    agent_name: str
    status: str
    summary: str
    metadata: Metadata = Field(default_factory=dict)


class BaseAgent:
    name: ClassVar[str] = "base-agent"

    async def run(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("GrantPilot agents are not implemented in this scaffold.")

