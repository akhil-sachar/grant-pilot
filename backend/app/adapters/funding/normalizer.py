from datetime import datetime, timezone

from app.adapters.funding.base import RawFundingRecord
from app.models import Opportunity, OpportunityType, RecordStatus


_TYPE_MAP: dict[str, OpportunityType] = {
    "scholarship": OpportunityType.SCHOLARSHIP,
    "grant": OpportunityType.GRANT,
    "fellowship": OpportunityType.FELLOWSHIP,
    "internship": OpportunityType.INTERNSHIP,
    "award": OpportunityType.AWARD,
}


def normalize_opportunity(record: RawFundingRecord) -> Opportunity:
    """Convert a raw funding record into the canonical Opportunity schema."""
    slug = record.source_name.lower().replace(" ", "_")
    opportunity_id = f"opp_{slug}_{record.external_id}"
    opportunity_type = _TYPE_MAP.get(record.opportunity_type.lower(), OpportunityType.GRANT)
    now = datetime.now(timezone.utc)

    metadata = {
        **record.metadata,
        "source": record.source_name,
        "funding_category": record.category.value,
        "external_id": record.external_id,
    }
    if record.fetched_at:
        metadata["fetched_at"] = record.fetched_at.isoformat()

    return Opportunity(
        id=opportunity_id,
        provider_name=record.provider_name,
        title=record.title,
        description=record.description,
        opportunity_type=opportunity_type,
        amount_min=record.amount_min,
        amount_max=record.amount_max,
        currency=record.currency,
        deadline=record.deadline,
        eligibility_summary=record.eligibility_summary,
        requirements=record.requirements,
        source_url=record.source_url,
        status=RecordStatus.ACTIVE,
        tags=[*record.tags, record.category.value],
        metadata=metadata,
        created_at=now,
        updated_at=now,
    )
