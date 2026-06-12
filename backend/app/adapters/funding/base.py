from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum

from pydantic import Field, HttpUrl

from app.models import APIModel, Metadata


class FundingCategory(str, Enum):
    FEDERAL_GRANT = "federal_grant"
    RESEARCH_GRANT = "research_grant"
    HEALTH_RESEARCH = "health_research"
    SBIR_STTR = "sbir_sttr"
    STARTUP_GRANT = "startup_grant"
    FOUNDATION = "foundation"
    UNIVERSITY = "university"
    SCHOLARSHIP = "scholarship"
    CORPORATE = "corporate"


class RawFundingRecord(APIModel):
    """Source-specific record before normalization into Opportunity."""

    external_id: str
    source_name: str
    category: FundingCategory
    provider_name: str
    title: str
    description: str
    opportunity_type: str
    amount_min: int | None = None
    amount_max: int | None = None
    currency: str = "USD"
    deadline: date | None = None
    eligibility_summary: str = ""
    requirements: list[str] = Field(default_factory=list)
    source_url: HttpUrl | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    fetched_at: datetime | None = None


class FundingSourceAdapter(ABC):
    """Adapter contract for external funding opportunity sources."""

    source_name: str
    category: FundingCategory

    @abstractmethod
    async def fetch_records(self) -> list[RawFundingRecord]:
        """Fetch raw opportunity records from the source."""

    @property
    def display_name(self) -> str:
        return self.source_name.replace("_", " ").title()
