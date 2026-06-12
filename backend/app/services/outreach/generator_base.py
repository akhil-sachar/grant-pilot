from abc import ABC, abstractmethod

from pydantic import Field

from app.models import APIModel, EmailType, Opportunity, RecipientRole, UserProfile


class OutreachGenerationInput(APIModel):
    profile: UserProfile
    opportunity: Opportunity
    recipient_role: RecipientRole
    email_type: EmailType
    recipient_email: str
    recipient_name: str = ""


class OutreachGenerationOutput(APIModel):
    subject: str
    body: str
    suggested_follow_up: str
    generation_method: str = "deterministic"


class OutreachGenerator(ABC):
    """Outreach email backend — swap in LLM generation later."""

    @abstractmethod
    def generate(self, outreach_input: OutreachGenerationInput) -> OutreachGenerationOutput:
        raise NotImplementedError
