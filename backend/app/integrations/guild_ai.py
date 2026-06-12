import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings


class GuildAIIntegration:
    """Tracks agent experiment runs for Guild AI observability."""

    TRACKED_AGENTS = frozenset(
        {
            "sponsor-agent",
            "matching-agent",
            "essay-agent",
            "recommendation-agent",
            "outreach-agent",
            "notification-agent",
            "composio-service",
        }
    )

    def __init__(self, settings: Settings):
        self.settings = settings
        self.guild_home = Path(settings.guild_home)
        if not self.guild_home.is_absolute():
            self.guild_home = (Path(__file__).resolve().parents[2] / settings.guild_home).resolve()
        self.enabled = settings.guild_ai_enabled

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Guild AI integration is disabled.")

    def _runs_path(self) -> Path:
        self.guild_home.mkdir(parents=True, exist_ok=True)
        return self.guild_home / "runs.jsonl"

    def begin_run(
        self,
        agent_name: str,
        action_type: str,
        *,
        user_id: str,
        input_summary: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        run_id = f"guild_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        if not self.enabled:
            return run_id

        record = {
            "run_id": run_id,
            "agent_name": agent_name,
            "action_type": action_type,
            "user_id": user_id,
            "status": "started",
            "input_summary": input_summary,
            "metadata": metadata or {},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_run(record)
        return run_id

    def complete_run(
        self,
        run_id: str,
        *,
        status: str,
        output_summary: str | None = None,
        runtime_ms: int | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return

        record = {
            "run_id": run_id,
            "status": status,
            "output_summary": output_summary,
            "runtime_ms": runtime_ms,
            "metrics": metrics or {},
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_run(record)

    def list_runs(self, *, agent_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        path = self._runs_path()
        if not path.exists():
            return []

        runs: dict[str, dict[str, Any]] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            run_id = record["run_id"]
            if run_id not in runs:
                runs[run_id] = {"run_id": run_id}
            runs[run_id].update(record)

        items = list(runs.values())
        if agent_name:
            items = [item for item in items if item.get("agent_name") == agent_name]
        items.sort(key=lambda item: item.get("started_at", ""), reverse=True)
        return items[:limit]

    def _append_run(self, record: dict[str, Any]) -> None:
        path = self._runs_path()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")


_guild: GuildAIIntegration | None = None


def get_guild_integration(settings: Settings | None = None) -> GuildAIIntegration:
    global _guild
    if settings is not None:
        return GuildAIIntegration(settings)
    if _guild is None:
        from app.config import get_settings

        _guild = GuildAIIntegration(get_settings())
    return _guild
