from app.models import EmailType, RecipientRole
from app.services.outreach.generator_base import (
    OutreachGenerationInput,
    OutreachGenerationOutput,
    OutreachGenerator,
)

_ROLE_GREETING: dict[RecipientRole, str] = {
    RecipientRole.PROFESSOR: "Dear Professor {name},",
    RecipientRole.ADVISOR: "Dear {name},",
    RecipientRole.SCHOLARSHIP_CONTACT: "Dear Scholarship Team,",
    RecipientRole.PROGRAM_DIRECTOR: "Dear Program Director,",
    RecipientRole.DEPARTMENT_HEAD: "Dear Department Head,",
}

_SUBJECT_TEMPLATES: dict[EmailType, str] = {
    EmailType.RECOMMENDATION_REQUEST: "Recommendation request — {opportunity}",
    EmailType.SCHOLARSHIP_INQUIRY: "Inquiry about {opportunity}",
    EmailType.ELIGIBILITY_QUESTION: "Eligibility question — {opportunity}",
    EmailType.FOLLOW_UP: "Following up on {opportunity}",
    EmailType.THANK_YOU: "Thank you — {opportunity} application support",
}


class DeterministicOutreachGenerator(OutreachGenerator):
    """Rule-based personalized outreach emails."""

    def generate(self, outreach_input: OutreachGenerationInput) -> OutreachGenerationOutput:
        profile = outreach_input.profile
        opportunity = outreach_input.opportunity
        student = profile.full_name
        role = outreach_input.recipient_role
        email_type = outreach_input.email_type
        recipient = outreach_input.recipient_name or _default_name(role)

        subject = _SUBJECT_TEMPLATES[email_type].format(opportunity=opportunity.title)
        greeting = _ROLE_GREETING[role].format(name=recipient)

        body = self._body_for_type(
            email_type=email_type,
            greeting=greeting,
            student=student,
            profile=profile,
            opportunity=opportunity,
            role=role,
        )
        suggested_follow_up = self._follow_up_for_type(email_type, opportunity.title, recipient)

        return OutreachGenerationOutput(
            subject=subject,
            body=body,
            suggested_follow_up=suggested_follow_up,
            generation_method="deterministic",
        )

    def _body_for_type(
        self,
        email_type: EmailType,
        greeting: str,
        student: str,
        profile,
        opportunity,
        role: RecipientRole,
    ) -> str:
        project = profile.projects[0] if profile.projects else "a community-focused software project"
        deadline = opportunity.deadline.isoformat() if opportunity.deadline else "the posted deadline"

        if email_type == EmailType.RECOMMENDATION_REQUEST:
            return (
                f"{greeting}\n\n"
                f"I hope you are doing well. I am writing to ask whether you would be willing to write a "
                f"recommendation letter for my application to {opportunity.title} "
                f"({opportunity.provider_name}).\n\n"
                f"The opportunity focuses on {opportunity.eligibility_summary.rstrip('.').lower()}. "
                f"My work on {project} aligns closely with this program, and I believe your perspective as "
                f"my {role.value.replace('_', ' ')} would strongly support my application.\n\n"
                f"I have attached a draft summary and can share my resume and project materials at your convenience. "
                f"The application deadline is {deadline}.\n\n"
                f"Thank you for considering this request.\n\n"
                f"Best regards,\n{student}\n{profile.email}"
            )

        if email_type == EmailType.SCHOLARSHIP_INQUIRY:
            return (
                f"{greeting}\n\n"
                f"My name is {student}, and I am a student at {profile.school_name or 'my institution'} "
                f"studying {profile.major or 'relevant fields'}. I am interested in {opportunity.title} "
                f"and would appreciate any guidance on how applicants are evaluated.\n\n"
                f"I am especially curious about expectations related to {', '.join(opportunity.tags[:3])} "
                f"and whether students with backgrounds like mine are competitive for this award.\n\n"
                f"Thank you for your time.\n\n"
                f"Sincerely,\n{student}\n{profile.email}"
            )

        if email_type == EmailType.ELIGIBILITY_QUESTION:
            return (
                f"{greeting}\n\n"
                f"I am preparing an application for {opportunity.title} and want to confirm my eligibility "
                f"before proceeding. Based on the published criteria ({opportunity.eligibility_summary.rstrip('.').lower()}), "
                f"I believe I may qualify, but I would appreciate clarification.\n\n"
                f"My background includes {profile.education_level or 'current enrollment'}, "
                f"a focus on {profile.major or 'relevant study'}, and experience with {project}.\n\n"
                f"Could you confirm whether I meet the requirements or if there are additional documents I should prepare?\n\n"
                f"Thank you,\n{student}\n{profile.email}"
            )

        if email_type == EmailType.FOLLOW_UP:
            return (
                f"{greeting}\n\n"
                f"I wanted to follow up regarding my earlier message about {opportunity.title}. "
                f"I remain very interested in the opportunity and am preparing my materials ahead of {deadline}.\n\n"
                f"Please let me know if you need any additional information from me, including updated project details "
                f"or supporting documents.\n\n"
                f"Best,\n{student}\n{profile.email}"
            )

        return (
            f"{greeting}\n\n"
            f"Thank you for your support and guidance as I work on my application for {opportunity.title}. "
            f"I appreciate the time you have taken to review my materials and answer my questions.\n\n"
            f"I will keep you updated on my progress and am grateful for your help.\n\n"
            f"Warm regards,\n{student}\n{profile.email}"
        )

    def _follow_up_for_type(self, email_type: EmailType, opportunity_title: str, recipient: str) -> str:
        if email_type == EmailType.RECOMMENDATION_REQUEST:
            return f"Follow up with {recipient} in 5–7 days if you have not received a response about {opportunity_title}."
        if email_type == EmailType.SCHOLARSHIP_INQUIRY:
            return "Send a brief follow-up in one week asking whether additional applicant materials would be helpful."
        if email_type == EmailType.ELIGIBILITY_QUESTION:
            return "If no reply within 4 business days, follow up with a concise restatement of your eligibility question."
        if email_type == EmailType.FOLLOW_UP:
            return "Schedule a final reminder two days before the application deadline."
        return f"Send a short thank-you note after {recipient} responds or after submission is complete."


def _default_name(role: RecipientRole) -> str:
    defaults = {
        RecipientRole.PROFESSOR: "Patel",
        RecipientRole.ADVISOR: "Lee",
        RecipientRole.SCHOLARSHIP_CONTACT: "Scholarship Team",
        RecipientRole.PROGRAM_DIRECTOR: "Program Director",
        RecipientRole.DEPARTMENT_HEAD: "Department Head",
    }
    return defaults[role]


class AIOutreachGenerator(OutreachGenerator):
    """Placeholder for future LLM-based outreach generation."""

    def generate(self, outreach_input: OutreachGenerationInput) -> OutreachGenerationOutput:
        raise NotImplementedError("AI outreach generation is not enabled yet.")
