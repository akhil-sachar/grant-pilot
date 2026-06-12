from pydantic import Field

from app.db.repository import GrantPilotRepository
from app.integrations.guild_ai import get_guild_integration
from app.models import APIModel, AgentActionLog, AgentActionStatus


TRACKED_AGENTS = [
    "sponsor-agent",
    "matching-agent",
    "essay-agent",
    "recommendation-agent",
    "outreach-agent",
    "notification-agent",
]


class AgentMetricSummary(APIModel):
    agent_name: str
    total_runs: int
    completed_runs: int
    failed_runs: int
    success_rate: float
    average_runtime_ms: float
    actions_completed: int
    opportunities_found: int = 0
    last_run_at: str | None = None


class AgentActivityResponse(APIModel):
    agents: list[AgentMetricSummary] = Field(default_factory=list)
    total_runs: int = 0
    overall_success_rate: float = 0.0
    average_runtime_ms: float = 0.0
    total_actions_completed: int = 0
    opportunities_found: int = 0
    recent_actions: list[AgentActionLog] = Field(default_factory=list)
    guild_runs: list[dict[str, object]] = Field(default_factory=list)


def _runtime_ms(log: AgentActionLog) -> int | None:
    value = log.metadata.get("runtime_ms")
    return int(value) if isinstance(value, (int, float)) else None


def _actions_from_log(log: AgentActionLog) -> int:
    metadata = log.metadata
    for key in ("matched", "created_count", "sources_scanned", "total_loaded", "actions"):
        value = metadata.get(key)
        if isinstance(value, int):
            return value
    if log.status == AgentActionStatus.COMPLETED:
        return 1
    return 0


def _opportunities_from_log(log: AgentActionLog) -> int:
    for key in ("total_loaded", "opportunities_found", "sources_scanned"):
        value = log.metadata.get(key)
        if isinstance(value, int):
            return value
    return 0


def build_agent_activity(storage: GrantPilotRepository, *, limit: int = 20) -> AgentActivityResponse:
    logs = storage.list_agent_action_logs()
    guild = get_guild_integration()
    opportunities = len(storage.list_opportunities())

    summaries: list[AgentMetricSummary] = []
    total_runs = 0
    total_completed = 0
    total_failed = 0
    runtime_values: list[int] = []
    total_actions = 0

    for agent_name in TRACKED_AGENTS:
        agent_logs = [log for log in logs if log.agent_name == agent_name]
        completed = [log for log in agent_logs if log.status == AgentActionStatus.COMPLETED]
        failed = [log for log in agent_logs if log.status == AgentActionStatus.FAILED]
        runtimes = [value for log in agent_logs if (value := _runtime_ms(log)) is not None]
        actions = sum(_actions_from_log(log) for log in completed)
        opp_found = sum(_opportunities_from_log(log) for log in completed if agent_name == "sponsor-agent")
        runs = len(agent_logs)
        success_rate = round(len(completed) / runs, 4) if runs else 0.0
        avg_runtime = round(sum(runtimes) / len(runtimes), 1) if runtimes else 0.0
        last_run = max((log.created_at for log in agent_logs), default=None)

        summaries.append(
            AgentMetricSummary(
                agent_name=agent_name,
                total_runs=runs,
                completed_runs=len(completed),
                failed_runs=len(failed),
                success_rate=success_rate,
                average_runtime_ms=avg_runtime,
                actions_completed=actions,
                opportunities_found=opp_found,
                last_run_at=last_run.isoformat() if last_run else None,
            )
        )

        total_runs += runs
        total_completed += len(completed)
        total_failed += len(failed)
        runtime_values.extend(runtimes)
        total_actions += actions

    overall_success = round(total_completed / total_runs, 4) if total_runs else 0.0
    overall_runtime = round(sum(runtime_values) / len(runtime_values), 1) if runtime_values else 0.0

    return AgentActivityResponse(
        agents=summaries,
        total_runs=total_runs,
        overall_success_rate=overall_success,
        average_runtime_ms=overall_runtime,
        total_actions_completed=total_actions,
        opportunities_found=opportunities,
        recent_actions=logs[:limit],
        guild_runs=guild.list_runs(limit=limit),
    )
