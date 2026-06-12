from datetime import date, datetime
from enum import Enum

from pydantic import Field, HttpUrl

from app.models.base import APIModel, Metadata, RecordStatus, utc_now


class OpportunityType(str, Enum):
    SCHOLARSHIP = "scholarship"
    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    INTERNSHIP = "internship"
    AWARD = "award"


class Opportunity(APIModel):
    id: str
    provider_name: str
    title: str
    description: str
    opportunity_type: OpportunityType
    amount_min: int | None = Field(default=None, ge=0)
    amount_max: int | None = Field(default=None, ge=0)
    currency: str = "USD"
    deadline: date | None = None
    eligibility_summary: str
    requirements: list[str] = Field(default_factory=list)
    source_url: HttpUrl | None = None
    status: RecordStatus = RecordStatus.ACTIVE
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

