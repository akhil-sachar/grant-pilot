from datetime import datetime, timezone

from app.adapters.funding.normalizer import normalize_opportunity
from app.adapters.funding.registry import get_all_adapters
from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.models import AgentActionLog, AgentActionStatus, Opportunity
from app.services.airbyte_service import AirbyteService
from app.services.scan_state import get_scan_tracker


class SponsorAgent(BaseAgent):
    """Continuously scans funding sources and stores normalized opportunities."""

    name = "sponsor-agent"

    def __init__(
        self,
        repository: GrantPilotRepository,
        airbyte_service: AirbyteService | None = None,
    ):
        self.repository = repository
        self.airbyte = airbyte_service or AirbyteService(repository=repository)
        self.tracker = get_scan_tracker()

    async def run(self, context: AgentContext) -> AgentResult:
        return await self.scan_all(context.user_id)

    async def scan_all(self, user_id: str = "usr_demo_001") -> AgentResult:
        action_id = f"agent_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        action_log = AgentActionLog(
            id=action_id,
            user_id=user_id,
            agent_name=self.name,
            action_type="full_scan",
            status=AgentActionStatus.STARTED,
            input_summary="Scanning all configured funding sources",
        )
        self.repository.create_record(action_log)

        airbyte_mode = "airbyte" if self.airbyte.is_configured else "mock"
        self.tracker.begin_full_scan(airbyte_mode=airbyte_mode)

        total_loaded = 0
        sources_scanned = 0
        errors: list[str] = []

        for adapter in get_all_adapters():
            self.tracker.begin_source_scan(adapter.source_name)
            try:
                raw_records = await self.airbyte.retrieve_records(adapter.source_name)
                opportunities = [normalize_opportunity(record) for record in raw_records]
                loaded = self._persist_opportunities(opportunities)

                run_id = f"ingest_{adapter.source_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
                from app.models import IngestionRun, IngestionRunStatus

                ingestion_run = IngestionRun(
                    id=run_id,
                    source_name=adapter.source_name,
                    status=IngestionRunStatus.COMPLETED,
                    records_seen=len(raw_records),
                    records_loaded=loaded,
                    metadata={"mode": airbyte_mode, "agent": self.name},
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                )
                self.repository.create_record(ingestion_run)
                self.tracker.complete_source_scan(adapter.source_name, loaded, run_id)
                total_loaded += loaded
                sources_scanned += 1
            except Exception as exc:
                errors.append(f"{adapter.source_name}: {exc}")
                self.tracker.fail_source_scan(adapter.source_name, str(exc))

        self.tracker.complete_full_scan()

        status = AgentActionStatus.COMPLETED if not errors else AgentActionStatus.FAILED
        summary = (
            f"Scanned {sources_scanned} sources, loaded {total_loaded} opportunities."
            if not errors
            else f"Scan finished with {len(errors)} errors. Loaded {total_loaded} opportunities."
        )
        self.repository.update_record(
            AgentActionLog,
            action_id,
            {
                "status": status,
                "output_summary": summary,
                "metadata": {"errors": errors, "sources_scanned": sources_scanned},
            },
        )

        return AgentResult(
            agent_name=self.name,
            status=status.value,
            summary=summary,
            metadata={
                "total_loaded": total_loaded,
                "sources_scanned": sources_scanned,
                "errors": errors,
                "airbyte_mode": airbyte_mode,
            },
        )

    async def scan_source(self, source_name: str, user_id: str = "usr_demo_001") -> AgentResult:
        from app.adapters.funding.registry import get_adapter

        adapter = get_adapter(source_name)
        if adapter is None:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                summary=f"Unknown source: {source_name}",
            )

        self.tracker.begin_source_scan(source_name)
        try:
            raw_records = await self.airbyte.retrieve_records(source_name)
            opportunities = [normalize_opportunity(record) for record in raw_records]
            loaded = self._persist_opportunities(opportunities)

            run_id = f"ingest_{source_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
            from app.models import IngestionRun, IngestionRunStatus

            ingestion_run = IngestionRun(
                id=run_id,
                source_name=source_name,
                status=IngestionRunStatus.COMPLETED,
                records_seen=len(raw_records),
                records_loaded=loaded,
                metadata={"mode": "airbyte" if self.airbyte.is_configured else "mock"},
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            self.repository.create_record(ingestion_run)
            self.tracker.complete_source_scan(source_name, loaded, run_id)

            return AgentResult(
                agent_name=self.name,
                status="completed",
                summary=f"Loaded {loaded} opportunities from {source_name}.",
                metadata={"records_loaded": loaded, "ingestion_run_id": run_id},
            )
        except Exception as exc:
            self.tracker.fail_source_scan(source_name, str(exc))
            return AgentResult(
                agent_name=self.name,
                status="failed",
                summary=str(exc),
            )

    def _persist_opportunities(self, opportunities: list[Opportunity]) -> int:
        loaded = 0
        for opportunity in opportunities:
            try:
                self.repository.get_opportunity(opportunity.id)
                self.repository.update_record(
                    Opportunity,
                    opportunity.id,
                    opportunity.model_dump(mode="json"),
                )
            except KeyError:
                self.repository.create_record(opportunity)
            loaded += 1
        return loaded
