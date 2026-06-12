from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field

from app.models.base import APIModel, Metadata, utc_now


class RecommendationStatus(str, Enum):
    NOT_STARTED = "not_started"
    DRAFTED = "drafted"
    SENT = "sent"
    RECEIVED = "received"


class RecommendationDraft(APIModel):
    id: str
    application_id: str
    recommender_name: str
    recommender_email: EmailStr
    relationship: str
    draft_body: str
    status: RecommendationStatus = RecommendationStatus.NOT_STARTED
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

