from datetime import datetime, timezone
from typing import Any

import httpx

from app.adapters.funding.base import RawFundingRecord
from app.adapters.funding.normalizer import normalize_opportunity
from app.config import Settings, get_settings
from app.db.repository import GrantPilotRepository
from app.models import IngestionRun, IngestionRunStatus, Opportunity


class AirbyteService:
    """Triggers Airbyte syncs, retrieves records, and logs ingestion runs."""

    def __init__(
        self,
        settings: Settings | None = None,
        repository: GrantPilotRepository | None = None,
    ):
        self.settings = settings or get_settings()
        self.repository = repository
        self.base_url = self.settings.airbyte_api_url.rstrip("/")
        self.api_key = self.settings.airbyte_api_key
        self.workspace_id = self.settings.airbyte_workspace_id

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.workspace_id)

    async def check_connection(self) -> bool:
        if not self.is_configured:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers(),
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def trigger_sync(self, connection_id: str) -> dict[str, Any]:
        if not self.is_configured:
            return {"status": "mock", "connection_id": connection_id}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/connections/sync",
                headers=self._headers(),
                json={"connectionId": connection_id},
            )
            response.raise_for_status()
            return response.json()

    async def retrieve_records(self, source_name: str) -> list[RawFundingRecord]:
        if await self.check_connection():
            try:
                return await self._fetch_from_airbyte(source_name)
            except httpx.HTTPError:
                pass
        return await self._adapter_fallback(source_name)

    async def run_ingestion(
        self,
        source_name: str,
        repository: GrantPilotRepository,
    ) -> tuple[IngestionRun, list[Opportunity]]:
        """Trigger sync, normalize records, persist opportunities, and log the run."""
        run_id = f"ingest_{source_name}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        run = IngestionRun(
            id=run_id,
            source_name=source_name,
            status=IngestionRunStatus.RUNNING,
            metadata={"airbyte_configured": self.is_configured},
            started_at=datetime.now(timezone.utc),
        )
        repository.create_record(run)

        try:
            if self.is_configured:
                connection_id = self.settings.airbyte_connection_ids.get(source_name, "")
                if connection_id:
                    await self.trigger_sync(connection_id)

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
                    "metadata": {
                        **run.metadata,
                        "mode": "airbyte" if self.is_configured else "mock",
                    },
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

    async def _fetch_from_airbyte(self, source_name: str) -> list[RawFundingRecord]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/sources/{source_name}/records",
                headers=self._headers(),
            )
            response.raise_for_status()
            payload = response.json()
        return [RawFundingRecord.model_validate(item) for item in payload.get("records", [])]

    async def _adapter_fallback(self, source_name: str) -> list[RawFundingRecord]:
        """Realistic fallback payloads shaped like Airbyte-synced records."""
        from app.adapters.funding.registry import get_adapter

        adapter = get_adapter(source_name)
        if adapter is None:
            return []
        return await adapter.fetch_records()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


def get_airbyte_service() -> AirbyteService:
    return AirbyteService()
