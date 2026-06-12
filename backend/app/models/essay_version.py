from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class EssayStatus(str, Enum):
    OUTLINE = "outline"
    DRAFT = "draft"
    REVIEW = "review"
    FINAL = "final"


class EssayVersion(APIModel):
    id: str
    application_id: str
    prompt: str
    content: str
    version_number: int = Field(ge=1)
    status: EssayStatus = EssayStatus.DRAFT
    feedback_notes: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

