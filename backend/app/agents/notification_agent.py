from pydantic import Field

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import APIModel, AgentActionStatus, Notification
from app.services.agent_run_tracker import get_agent_run_tracker
from app.services.notification_service import build_notification_candidates


class NotificationRunResult(APIModel):
    created_count: int
    notifications: list[Notification] = Field(default_factory=list)


class NotificationAgent(BaseAgent):
    """Generates actionable notifications from opportunities, matches, and application state."""

    name = "notification-agent"

    def __init__(self, repository: GrantPilotRepository):
        self.repository = repository

    async def run(self, context: AgentContext) -> AgentResult:
        result = await self.generate_notifications(context.user_id)
        return AgentResult(
            agent_name=self.name,
            status="completed",
            summary=f"Created {result.created_count} notifications.",
            metadata={"created_count": result.created_count},
        )

    async def generate_notifications(self, user_id: str = DEFAULT_USER_ID) -> NotificationRunResult:
        tracker = get_agent_run_tracker(self.repository)
        action_id = tracker.start(
            user_id,
            self.name,
            "generate_notifications",
            "Scanning workspace for notification events",
        )

        candidates = build_notification_candidates(self.repository, user_id)
        created: list[Notification] = []
        for notification in candidates:
            self.repository.create_record(notification)
            created.append(notification)

        tracker.finish(
            action_id,
            status=AgentActionStatus.COMPLETED,
            output_summary=f"Created {len(created)} notifications.",
            metadata={"created_count": len(created)},
        )

        return NotificationRunResult(created_count=len(created), notifications=created)
