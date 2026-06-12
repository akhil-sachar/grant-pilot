from datetime import datetime
from enum import Enum

from pydantic import Field, computed_field

from app.models.base import APIModel, Metadata, utc_now


class MatchStatus(str, Enum):
    NEW = "new"
    SAVED = "saved"
    DISMISSED = "dismissed"
    IN_APPLICATION = "in_application"


class MatchPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MatchResult(APIModel):
    id: str
    user_id: str
    opportunity_id: str
    score: float = Field(ge=0, le=1, description="Normalized match score (0–1)")
    rationale: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    priority: MatchPriority = MatchPriority.MEDIUM
    missing_materials: list[str] = Field(default_factory=list)
    fit_explanation: str = ""
    funding_potential: str = ""
    success_probability: float = Field(default=0, ge=0, le=1)
    status: MatchStatus = MatchStatus.NEW
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def score_percent(self) -> int:
        return round(self.score * 100)
