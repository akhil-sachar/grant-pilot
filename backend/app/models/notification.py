from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class NotificationType(str, Enum):
    DEADLINE = "deadline"
    DOCUMENT = "document"
    MATCH = "match"
    APPLICATION = "application"
    SYSTEM = "system"


class Notification(APIModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType = NotificationType.SYSTEM
    is_read: bool = False
    action_url: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

