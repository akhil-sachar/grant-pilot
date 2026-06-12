import time
from datetime import datetime, timezone
from typing import Any

from app.config import get_settings
from app.db.repository import GrantPilotRepository
from app.integrations.guild_ai import get_guild_integration
from app.models import AgentActionLog, AgentActionStatus


class AgentRunTracker:
    """Unified AgentActionLog + Guild AI tracking for autonomous agents."""

    def __init__(self, repository: GrantPilotRepository):
        self.repository = repository
        self.guild = get_guild_integration()
        self._started_at: dict[str, float] = {}

    def start(
        self,
        user_id: str,
        agent_name: str,
        action_type: str,
        input_summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        action_id = f"agent_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        guild_run_id = self.guild.begin_run(
            agent_name,
            action_type,
            user_id=user_id,
            input_summary=input_summary,
            metadata=metadata,
        )
        payload = dict(metadata or {})
        payload["guild_run_id"] = guild_run_id
        payload["tracked_by"] = "guild-ai"

        action_log = AgentActionLog(
            id=action_id,
            user_id=user_id,
            agent_name=agent_name,
            action_type=action_type,
            status=AgentActionStatus.STARTED,
            input_summary=input_summary,
            metadata=payload,
        )
        self.repository.create_record(action_log)
        self._started_at[action_id] = time.perf_counter()
        return action_id

    def finish(
        self,
        action_id: str,
        *,
        status: AgentActionStatus,
        output_summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        started = self._started_at.pop(action_id, None)
        runtime_ms = int((time.perf_counter() - started) * 1000) if started is not None else None

        existing = self.repository.get_record(AgentActionLog, action_id)
        merged_metadata = dict(existing.metadata)
        merged_metadata.update(metadata or {})
        if runtime_ms is not None:
            merged_metadata["runtime_ms"] = runtime_ms

        guild_run_id = merged_metadata.get("guild_run_id")
        if isinstance(guild_run_id, str):
            self.guild.complete_run(
                guild_run_id,
                status=status.value,
                output_summary=output_summary,
                runtime_ms=runtime_ms,
                metrics={k: v for k, v in merged_metadata.items() if k != "guild_run_id"},
            )

        self.repository.update_record(
            AgentActionLog,
            action_id,
            {
                "status": status,
                "output_summary": output_summary,
                "metadata": merged_metadata,
            },
        )


def get_agent_run_tracker(repository: GrantPilotRepository) -> AgentRunTracker:
    get_settings()
    return AgentRunTracker(repository)
