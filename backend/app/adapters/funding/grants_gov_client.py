from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any

import httpx

from app.adapters.funding.base import FundingCategory, RawFundingRecord
from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _parse_us_date(value: str | None) -> date | None:
    if not value or not value.strip():
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _hit_to_record(hit: dict[str, Any], source_name: str, category: FundingCategory) -> RawFundingRecord:
    opp_id = str(hit.get("id", ""))
    opp_number = str(hit.get("number", opp_id))
    agency_name = str(hit.get("agencyName") or hit.get("agencyCode") or "U.S. Federal Agency")
    title = str(hit.get("title") or "Untitled opportunity")
    status = str(hit.get("oppStatus") or "posted")
    doc_type = str(hit.get("docType") or "synopsis")
    aln_list = hit.get("alnist") or hit.get("alnList") or []
    aln_tags = [str(item) for item in aln_list if item]

    description = (
        f"Federal funding opportunity {opp_number} from {agency_name}. "
        f"Status: {status}. Document type: {doc_type}."
    )
    if aln_tags:
        description += f" ALN: {', '.join(aln_tags[:3])}."

    detail_url = f"https://www.grants.gov/search-results-detail/{opp_id}" if opp_id else None

    return RawFundingRecord(
        external_id=opp_number or opp_id,
        source_name=source_name,
        category=category,
        provider_name=agency_name,
        title=title,
        description=description,
        opportunity_type="grant",
        deadline=_parse_us_date(hit.get("closeDate")),
        eligibility_summary=f"See Grants.gov listing {opp_number} for eligibility requirements.",
        requirements=["Review full synopsis on Grants.gov"],
        source_url=detail_url,
        tags=["federal", "grants-gov", status, *aln_tags[:2]],
        metadata={
            "grants_gov_id": opp_id,
            "opportunity_number": opp_number,
            "agency_code": hit.get("agencyCode"),
            "open_date": hit.get("openDate"),
            "opp_status": status,
            "doc_type": doc_type,
            "aln_list": aln_tags,
            "live_api": True,
        },
        fetched_at=datetime.now(timezone.utc),
    )


class GrantsGovClient:
    """Client for the Grants.gov search2 API (no auth required).

    Docs: https://www.grants.gov/api/common/search2
    Endpoint: POST https://api.grants.gov/v1/api/search2
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.grants_gov_live_enabled

    async def search_opportunities(self) -> list[RawFundingRecord]:
        if not self.enabled:
            return []

        payload = {
            "rows": self.settings.grants_gov_search_rows,
            "keyword": self.settings.grants_gov_search_keyword,
            "oppNum": "",
            "eligibilities": "",
            "agencies": self.settings.grants_gov_search_agencies,
            "oppStatuses": self.settings.grants_gov_opp_statuses,
            "aln": "",
            "fundingCategories": self.settings.grants_gov_funding_categories,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.settings.grants_gov_api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            body = response.json()

        if body.get("errorcode") not in (0, "0", None):
            raise RuntimeError(f"Grants.gov API error: {body.get('msg', body)}")

        data = body.get("data") or {}
        hits = data.get("oppHits") or []
        records = [
            _hit_to_record(hit, "grants_gov", FundingCategory.FEDERAL_GRANT)
            for hit in hits
            if hit.get("id") or hit.get("number")
        ]
        logger.info("Grants.gov search2 returned %s opportunities", len(records))
        return records


async def fetch_grants_gov_records(fallback: list[RawFundingRecord]) -> list[RawFundingRecord]:
    """Fetch live Grants.gov records, falling back to embedded samples on failure."""
    client = GrantsGovClient()
    if not client.enabled:
        return fallback

    try:
        records = await client.search_opportunities()
        return records if records else fallback
    except Exception:
        logger.exception("Grants.gov live fetch failed; using adapter fallback records")
        return fallback
