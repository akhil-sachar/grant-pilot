from pydantic import Field

from app.db.repository import GrantPilotRepository
from app.models import (
    APIModel,
    Application,
    EssayVersion,
    Opportunity,
    OutreachEmail,
    RecommendationDraft,
)


class ApplicationBundle(APIModel):
    application: Application
    opportunity: Opportunity
    essay_versions: list[EssayVersion] = Field(default_factory=list)
    recommendation_drafts: list[RecommendationDraft] = Field(default_factory=list)
    outreach_emails: list[OutreachEmail] = Field(default_factory=list)


def build_application_bundle(
    storage: GrantPilotRepository,
    application_id: str,
) -> ApplicationBundle:
    application = storage.get_application(application_id)
    return ApplicationBundle(
        application=application,
        opportunity=storage.get_opportunity(application.opportunity_id),
        essay_versions=storage.list_essay_versions(application_id),
        recommendation_drafts=storage.list_recommendation_drafts(application_id),
        outreach_emails=storage.list_outreach_emails(application_id),
    )
