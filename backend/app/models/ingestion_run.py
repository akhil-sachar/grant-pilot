from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class IngestionRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionRun(APIModel):
    id: str
    source_name: str
    status: IngestionRunStatus = IngestionRunStatus.QUEUED
    records_seen: int = Field(default=0, ge=0)
    records_loaded: int = Field(default=0, ge=0)
    error_message: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None

