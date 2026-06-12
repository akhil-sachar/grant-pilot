from app.models import EmailType, Opportunity, OutreachEmail, RecipientRole, UserProfile
from app.services.outreach.deterministic_generator import AIOutreachGenerator, DeterministicOutreachGenerator
from app.services.outreach.generator_base import OutreachGenerationInput, OutreachGenerationOutput, OutreachGenerator

_DEFAULT_RECIPIENTS: dict[RecipientRole, tuple[str, str]] = {
    RecipientRole.PROFESSOR: ("Dr. Ana Patel", "apatel@example.edu"),
    RecipientRole.ADVISOR: ("Jordan Lee", "jlee@example.edu"),
    RecipientRole.SCHOLARSHIP_CONTACT: ("Scholarship Office", "scholarships@example.org"),
    RecipientRole.PROGRAM_DIRECTOR: ("Program Director", "director@example.edu"),
    RecipientRole.DEPARTMENT_HEAD: ("Department Head", "depthead@example.edu"),
}


def get_outreach_generator(method: str = "deterministic") -> OutreachGenerator:
    if method == "ai":
        return AIOutreachGenerator()
    return DeterministicOutreachGenerator()


def resolve_recipient(role: RecipientRole, name: str | None = None, email: str | None = None) -> tuple[str, str]:
    default_name, default_email = _DEFAULT_RECIPIENTS[role]
    return name or default_name, email or default_email


def generate_outreach_email(
    profile: UserProfile,
    opportunity: Opportunity,
    recipient_role: RecipientRole,
    email_type: EmailType,
    recipient_name: str | None = None,
    recipient_email: str | None = None,
    method: str = "deterministic",
) -> OutreachGenerationOutput:
    name, email = resolve_recipient(recipient_role, recipient_name, recipient_email)
    generator = get_outreach_generator(method)
    return generator.generate(
        OutreachGenerationInput(
            profile=profile,
            opportunity=opportunity,
            recipient_role=recipient_role,
            email_type=email_type,
            recipient_email=email,
            recipient_name=name,
        )
    )


def next_email_version(existing: list[OutreachEmail]) -> int:
    if not existing:
        return 1
    return max(email.version_number for email in existing) + 1
