from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from app.adapters.funding.registry import get_all_adapters
from app.models.sponsor_scan import SourceScanState, SourceScanStatus, SponsorScanStatus


class ScanStateTracker:
    """In-memory tracker for real-time sponsor scan status."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._is_scanning = False
        self._last_full_scan_at: datetime | None = None
        self._airbyte_mode = "mock"
        self._sources: dict[str, SourceScanState] = {}
        self._initialize_sources()

    def _initialize_sources(self) -> None:
        for adapter in get_all_adapters():
            self._sources[adapter.source_name] = SourceScanState(
                source_name=adapter.source_name,
                display_name=adapter.display_name,
                category=adapter.category.value,
            )

    def begin_full_scan(self, airbyte_mode: str = "mock") -> None:
        with self._lock:
            self._is_scanning = True
            self._airbyte_mode = airbyte_mode
            for source in self._sources.values():
                source.status = SourceScanStatus.SCANNING
                source.error_message = None

    def begin_source_scan(self, source_name: str) -> None:
        with self._lock:
            source = self._sources.get(source_name)
            if source:
                source.status = SourceScanStatus.SCANNING
                source.error_message = None

    def complete_source_scan(
        self,
        source_name: str,
        opportunities_found: int,
        ingestion_run_id: str,
    ) -> None:
        with self._lock:
            source = self._sources.get(source_name)
            if source:
                source.status = SourceScanStatus.COMPLETED
                source.opportunities_found = opportunities_found
                source.last_scan_at = datetime.now(timezone.utc)
                source.last_ingestion_run_id = ingestion_run_id
                source.error_message = None

    def fail_source_scan(self, source_name: str, error_message: str) -> None:
        with self._lock:
            source = self._sources.get(source_name)
            if source:
                source.status = SourceScanStatus.FAILED
                source.error_message = error_message
                source.last_scan_at = datetime.now(timezone.utc)

    def complete_full_scan(self) -> None:
        with self._lock:
            self._is_scanning = False
            self._last_full_scan_at = datetime.now(timezone.utc)

    def snapshot(
        self,
        total_opportunities: int,
        recent_ingestion_runs: list,
    ) -> SponsorScanStatus:
        with self._lock:
            return SponsorScanStatus(
                is_scanning=self._is_scanning,
                last_full_scan_at=self._last_full_scan_at,
                total_opportunities=total_opportunities,
                sources=list(self._sources.values()),
                recent_ingestion_runs=recent_ingestion_runs,
                airbyte_mode=self._airbyte_mode,
                updated_at=datetime.now(timezone.utc),
            )


_scan_tracker: ScanStateTracker | None = None


def get_scan_tracker() -> ScanStateTracker:
    global _scan_tracker
    if _scan_tracker is None:
        _scan_tracker = ScanStateTracker()
    return _scan_tracker
