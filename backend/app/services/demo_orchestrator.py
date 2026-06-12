import asyncio
from datetime import datetime, timezone

from pydantic import Field

from app.agents.base import AgentContext
from app.agents.essay_agent import EssayAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.outreach_agent import OutreachAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.sponsor_agent import SponsorAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import APIModel, AgentActionLog
from app.services.composio_service import get_composio_service


class DemoStepResult(APIModel):
    step: str
    agent_name: str
    status: str
    summary: str
    metadata: dict[str, object] = Field(default_factory=dict)


class DemoRunResult(APIModel):
    started_at: str
    completed_at: str
    steps: list[DemoStepResult] = Field(default_factory=list)
    agent_actions: list[AgentActionLog] = Field(default_factory=list)


async def run_demo_pipeline(
    repository: GrantPilotRepository,
    user_id: str = DEFAULT_USER_ID,
) -> DemoRunResult:
    started = datetime.now(timezone.utc)
    steps: list[DemoStepResult] = []
    context = AgentContext(user_id=user_id)

    sponsor = SponsorAgent(repository)
    result = await sponsor.run(context)
    steps.append(
        DemoStepResult(
            step="opportunity_discovery",
            agent_name=sponsor.name,
            status=result.status,
            summary=result.summary,
            metadata=result.metadata,
        )
    )
    await asyncio.sleep(0.2)

    matching = MatchingAgent(repository)
    result = await matching.run(context)
    steps.append(
        DemoStepResult(
            step="matching",
            agent_name=matching.name,
            status=result.status,
            summary=result.summary,
            metadata=result.metadata,
        )
    )
    await asyncio.sleep(0.2)

    applications = repository.list_applications(user_id)
    civic_app = next((item for item in applications if "civic" in item.id), applications[0] if applications else None)
    open_app = next((item for item in applications if "open" in item.id), applications[-1] if applications else None)

    if civic_app:
        essay = EssayAgent(repository)
        essay_context = AgentContext(user_id=user_id, application_id=civic_app.id)
        result = await essay.run(essay_context)
        steps.append(
            DemoStepResult(
                step="essay_improvement",
                agent_name=essay.name,
                status=result.status,
                summary=result.summary,
                metadata=result.metadata,
            )
        )
        await asyncio.sleep(0.2)

    if open_app:
        recommendation = RecommendationAgent(repository)
        rec_context = AgentContext(user_id=user_id, application_id=open_app.id)
        result = await recommendation.run(rec_context)
        steps.append(
            DemoStepResult(
                step="recommendation_generation",
                agent_name=recommendation.name,
                status=result.status,
                summary=result.summary,
                metadata=result.metadata,
            )
        )
        await asyncio.sleep(0.2)

        outreach = OutreachAgent(repository)
        outreach_context = AgentContext(user_id=user_id, application_id=open_app.id)
        result = await outreach.run(outreach_context)
        steps.append(
            DemoStepResult(
                step="personalized_outreach",
                agent_name=outreach.name,
                status=result.status,
                summary=result.summary,
                metadata=result.metadata,
            )
        )
        await asyncio.sleep(0.2)

    notification = NotificationAgent(repository)
    result = await notification.run(context)
    steps.append(
        DemoStepResult(
            step="notification_creation",
            agent_name=notification.name,
            status=result.status,
            summary=result.summary,
            metadata=result.metadata,
        )
    )

    composio = get_composio_service()
    composio_status = composio.status()
    steps.append(
        DemoStepResult(
            step="composio_actions",
            agent_name="composio-service",
            status="completed",
            summary=f"Composio running in {composio_status.mode.value} mode.",
            metadata=composio_status.model_dump(mode="json"),
        )
    )

    completed = datetime.now(timezone.utc)
    recent_logs = repository.list_agent_action_logs()[:12]

    return DemoRunResult(
        started_at=started.isoformat(),
        completed_at=completed.isoformat(),
        steps=steps,
        agent_actions=recent_logs,
    )
