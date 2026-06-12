from __future__ import annotations

import json
from typing import Any

from app.models import Opportunity, UserProfile, UploadedDocument


def profile_summary(profile: UserProfile) -> str:
    return json.dumps(
        {
            "full_name": profile.full_name,
            "major": profile.major,
            "gpa": profile.gpa,
            "education_level": profile.education_level,
            "school_name": profile.school_name,
            "career_goals": profile.career_goals,
            "research_interests": profile.research_interests,
            "projects": profile.projects,
            "awards": profile.awards,
            "leadership_experience": profile.leadership_experience,
            "fields_of_study": profile.fields_of_study,
            "funding_goals": profile.funding_goals,
        },
        indent=2,
    )


def opportunity_summary(opportunity: Opportunity) -> str:
    return json.dumps(
        {
            "id": opportunity.id,
            "title": opportunity.title,
            "provider_name": opportunity.provider_name,
            "description": opportunity.description,
            "eligibility_summary": opportunity.eligibility_summary,
            "requirements": opportunity.requirements,
            "tags": opportunity.tags,
            "amount_min": opportunity.amount_min,
            "amount_max": opportunity.amount_max,
            "deadline": opportunity.deadline.isoformat() if opportunity.deadline else None,
            "opportunity_type": opportunity.opportunity_type.value,
        },
        indent=2,
    )


def document_summary(document: UploadedDocument | None, label: str) -> str:
    if document is None:
        return f"{label}: not uploaded"
    preview = document.extracted_text_preview or document.extracted_text or ""
    return f"{label} ({document.document_type.value}, status={document.status.value}): {preview[:1200]}"
