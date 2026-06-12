from __future__ import annotations

from app.models import Opportunity
from app.services.llm.context import opportunity_summary
from app.services.llm.openai_service import get_openai_service


def enrich_opportunity(opportunity: Opportunity) -> Opportunity:
    """Use OpenAI to refine opportunity copy for discovery feeds."""
    llm = get_openai_service()
    if not llm.enabled:
        return opportunity

    try:
        data = llm.chat_json(
            agent_name="sponsor-agent",
            action="enrich_opportunity",
            system_prompt=(
                "Improve funding opportunity listings for students. "
                "Return JSON: description (string, 2-3 sentences), "
                "eligibility_summary (string, 1-2 sentences), tags (string[])."
            ),
            user_prompt=f"Opportunity:\n{opportunity_summary(opportunity)}",
        )
        updates = opportunity.model_dump(mode="json")
        if data.get("description"):
            updates["description"] = str(data["description"])
        if data.get("eligibility_summary"):
            updates["eligibility_summary"] = str(data["eligibility_summary"])
        if data.get("tags"):
            updates["tags"] = [str(tag) for tag in data["tags"]]
        updates["metadata"] = {
            **opportunity.metadata,
            "openai_enriched": True,
            "generation_method": "openai",
        }
        return Opportunity.model_validate(updates)
    except Exception:
        return opportunity
