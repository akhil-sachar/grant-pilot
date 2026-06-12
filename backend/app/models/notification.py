from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class NotificationType(str, Enum):
    NEW_OPPORTUNITY = "new_opportunity"
    HIGH_MATCH = "high_match"
    DEADLINE_APPROACHING = "deadline_approaching"
    MISSING_DOCUMENT = "missing_document"
    ESSAY_READY = "essay_ready"
    RECOMMENDATION_READY = "recommendation_ready"
    EMAIL_DRAFT_READY = "email_draft_ready"
    DEADLINE = "deadline"
    DOCUMENT = "document"
    MATCH = "match"
    APPLICATION = "application"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(APIModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType = NotificationType.SYSTEM
    priority: NotificationPriority = NotificationPriority.MEDIUM
    is_read: bool = False
    action_url: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
