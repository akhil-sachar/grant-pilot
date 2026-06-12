from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class ApplicationStatus(str, Enum):
    DISCOVERED = "discovered"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"
    DECLINED = "declined"


class ChecklistItemStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class ApplicationChecklistItem(APIModel):
    id: str
    label: str
    status: ChecklistItemStatus = ChecklistItemStatus.TODO
    due_at: datetime | None = None


class Application(APIModel):
    id: str
    user_id: str
    opportunity_id: str
    match_result_id: str | None = None
    status: ApplicationStatus = ApplicationStatus.PLANNED
    due_at: datetime | None = None
    submitted_at: datetime | None = None
    checklist: list[ApplicationChecklistItem] = Field(default_factory=list)
    notes: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

