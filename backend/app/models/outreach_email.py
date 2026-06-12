from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field

from app.models.base import APIModel, Metadata, utc_now


class OutreachEmailStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class OutreachEmail(APIModel):
    id: str
    application_id: str
    recipient_email: EmailStr
    subject: str
    body: str
    status: OutreachEmailStatus = OutreachEmailStatus.DRAFT
    sent_at: datetime | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

