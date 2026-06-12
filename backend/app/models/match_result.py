from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class MatchStatus(str, Enum):
    NEW = "new"
    SAVED = "saved"
    DISMISSED = "dismissed"
    IN_APPLICATION = "in_application"


class MatchResult(APIModel):
    id: str
    user_id: str
    opportunity_id: str
    score: float = Field(ge=0, le=1)
    rationale: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    status: MatchStatus = MatchStatus.NEW
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

