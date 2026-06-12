from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class AgentActionStatus(str, Enum):
    PLANNED = "planned"
    SKIPPED = "skipped"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentActionLog(APIModel):
    id: str
    user_id: str
    agent_name: str
    action_type: str
    status: AgentActionStatus = AgentActionStatus.PLANNED
    input_summary: str | None = None
    output_summary: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

