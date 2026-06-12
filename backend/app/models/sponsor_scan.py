from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models import APIModel, IngestionRun, Metadata, utc_now


class SourceScanStatus(str, Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceScanState(APIModel):
    source_name: str
    display_name: str
    category: str
    status: SourceScanStatus = SourceScanStatus.IDLE
    opportunities_found: int = 0
    last_scan_at: datetime | None = None
    last_ingestion_run_id: str | None = None
    error_message: str | None = None


class SponsorScanStatus(APIModel):
    is_scanning: bool = False
    last_full_scan_at: datetime | None = None
    total_opportunities: int = 0
    sources: list[SourceScanState] = Field(default_factory=list)
    recent_ingestion_runs: list[IngestionRun] = Field(default_factory=list)
    airbyte_mode: str = "mock"
    metadata: Metadata = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=utc_now)
