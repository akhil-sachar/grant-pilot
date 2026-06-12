from datetime import datetime, timezone

from app.adapters.funding.base import RawFundingRecord
from app.adapters.funding.normalizer import normalize_opportunity
from app.adapters.funding.registry import get_adapter
from app.db.repository import GrantPilotRepository
from app.models import IngestionRun, IngestionRunStatus, Opportunity


class FundingIngestionService:
    """Fetches funding records from source adapters and persists opportunities."""

    async def retrieve_records(self, source_name: str) -> list[RawFundingRecord]:
        adapter = get_adapter(source_name)
        if adapter is None:
            return []
        return await adapter.fetch_records()

    async def run_ingestion(
        self,
        source_name: str,
        repository: GrantPilotRepository,
    ) -> tuple[IngestionRun, list[Opportunity]]:
        run_id = f"ingest_{source_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        run = IngestionRun(
            id=run_id,
            source_name=source_name,
            status=IngestionRunStatus.RUNNING,
            metadata={"mode": "adapter", "agent": "sponsor-agent"},
            started_at=datetime.now(timezone.utc),
        )
        repository.create_record(run)

        try:
            raw_records = await self.retrieve_records(source_name)
            opportunities = [normalize_opportunity(record) for record in raw_records]
            loaded = 0
            for opportunity in opportunities:
                try:
                    repository.get_opportunity(opportunity.id)
                    repository.update_record(
                        Opportunity,
                        opportunity.id,
                        opportunity.model_dump(mode="json"),
                    )
                except KeyError:
                    repository.create_record(opportunity)
                loaded += 1

            completed = run.model_copy(
                update={
                    "status": IngestionRunStatus.COMPLETED,
                    "records_seen": len(raw_records),
                    "records_loaded": loaded,
                    "metadata": {**run.metadata, "mode": "adapter"},
                    "completed_at": datetime.now(timezone.utc),
                }
            )
            repository.update_record(IngestionRun, run_id, completed.model_dump(mode="json"))
            return completed, opportunities
        except Exception as exc:
            failed = run.model_copy(
                update={
                    "status": IngestionRunStatus.FAILED,
                    "error_message": str(exc),
                    "completed_at": datetime.now(timezone.utc),
                }
            )
            repository.update_record(IngestionRun, run_id, failed.model_dump(mode="json"))
            raise


def get_funding_ingestion_service() -> FundingIngestionService:
    return FundingIngestionService()
