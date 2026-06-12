from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field

from app.models.base import APIModel, Metadata, utc_now


class OutreachEmailStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class RecipientRole(str, Enum):
    PROFESSOR = "professor"
    ADVISOR = "advisor"
    SCHOLARSHIP_CONTACT = "scholarship_contact"
    PROGRAM_DIRECTOR = "program_director"
    DEPARTMENT_HEAD = "department_head"


class EmailType(str, Enum):
    RECOMMENDATION_REQUEST = "recommendation_request"
    SCHOLARSHIP_INQUIRY = "scholarship_inquiry"
    ELIGIBILITY_QUESTION = "eligibility_question"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"


class OutreachEmail(APIModel):
    id: str
    application_id: str
    recipient_email: EmailStr
    recipient_role: RecipientRole = RecipientRole.PROFESSOR
    email_type: EmailType = EmailType.RECOMMENDATION_REQUEST
    subject: str
    body: str
    suggested_follow_up: str = ""
    version_number: int = Field(default=1, ge=1)
    source_email_id: str | None = None
    status: OutreachEmailStatus = OutreachEmailStatus.DRAFT
    sent_at: datetime | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
