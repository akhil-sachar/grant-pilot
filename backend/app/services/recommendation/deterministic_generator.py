from app.models import RecommenderType
from app.models.recommendation_draft import DRAFT_REVIEW_BANNER
from app.services.recommendation.generator_base import (
    RecommendationGenerationInput,
    RecommendationGenerationOutput,
    RecommendationGenerator,
)

_VOICE_BY_TYPE: dict[RecommenderType, str] = {
    RecommenderType.PROFESSOR: "As their instructor and research mentor",
    RecommenderType.ADVISOR: "As their academic advisor",
    RecommenderType.MENTOR: "As a mentor who has worked closely with them",
    RecommenderType.MANAGER: "As their supervisor on applied project work",
}


class DeterministicRecommendationGenerator(RecommendationGenerator):
    """Rule-based recommendation draft tailored to opportunity criteria."""

    def generate(self, rec_input: RecommendationGenerationInput) -> RecommendationGenerationOutput:
        profile = rec_input.profile
        opportunity = rec_input.opportunity
        student = profile.full_name
        voice = _VOICE_BY_TYPE[rec_input.recommender_type]
        gpa_line = f"GPA {profile.gpa}" if profile.gpa else "strong academic performance"
        project = profile.projects[0] if profile.projects else "community-focused software work"
        research = profile.research_interests[0] if profile.research_interests else "public-interest technology"

        talking_points = [
            f"{student}'s {gpa_line} and coursework in {profile.major or 'their program'}.",
            f"Demonstrated execution on {project}.",
            f"Clear alignment with {opportunity.title} through {research.lower()}.",
            f"Reliability, initiative, and fit for {opportunity.provider_name}'s selection criteria.",
        ]
        if rec_input.transcript_text:
            talking_points.append("Academic record shows consistent preparation in relevant coursework.")
        if rec_input.existing_letters:
            talking_points.append("Prior recommendation materials highlight discipline and follow-through.")

        why_it_matches = (
            f"{student} meets {opportunity.title} criteria through {opportunity.eligibility_summary.rstrip('.').lower()}, "
            f"with project experience that maps to tags such as {', '.join(opportunity.tags[:3])}."
        )

        opening = (
            f"Dear Selection Committee,\n\n"
            f"{voice}, I am pleased to recommend {student} for {opportunity.title} "
            f"offered by {opportunity.provider_name}."
        )
        body = (
            f"{opening}\n\n"
            f"In my experience, {student} combines analytical rigor with a sustained commitment to "
            f"{profile.career_goals[0].lower() if profile.career_goals else 'meaningful community impact'}. "
            f"Their work on {project} shows they can translate ideas into usable outcomes.\n\n"
            f"This opportunity emphasizes {opportunity.description.split('.')[0].lower()}. "
            f"{student} is especially prepared to contribute because of their background in "
            f"{profile.major or 'relevant study'} and their track record of delivering practical results.\n\n"
            f"I recommend {student} without reservation for this award and believe they will represent "
            f"{opportunity.provider_name} with integrity and impact."
        )
        closing = f"\n\nSincerely,\n{rec_input.recommender_name}\n{rec_input.relationship}"

        draft_body = f"{DRAFT_REVIEW_BANNER}\n{body}{closing}"

        return RecommendationGenerationOutput(
            draft_body=draft_body,
            key_talking_points=talking_points,
            why_it_matches=why_it_matches,
            generation_method="deterministic",
        )


class AIRecommendationGenerator(RecommendationGenerator):
    """OpenAI-powered recommendation drafts with Langfuse tracing."""

    def generate(self, rec_input: RecommendationGenerationInput) -> RecommendationGenerationOutput:
        from app.services.llm.context import opportunity_summary, profile_summary
        from app.services.llm.openai_service import get_openai_service

        llm = get_openai_service()
        fallback = DeterministicRecommendationGenerator()
        try:
            data = llm.chat_json(
                agent_name="recommendation-agent",
                action="generate_recommendation",
                system_prompt=(
                    "Draft a recommendation letter FOR the recommender to review and edit. "
                    "Include the banner line exactly as first line: "
                    f"\"{DRAFT_REVIEW_BANNER}\" "
                    "Return JSON: draft_body (string), key_talking_points (string[]), why_it_matches (string)."
                ),
                user_prompt=(
                    f"Student profile:\n{profile_summary(rec_input.profile)}\n\n"
                    f"Opportunity:\n{opportunity_summary(rec_input.opportunity)}\n\n"
                    f"Recommender: {rec_input.recommender_name} ({rec_input.recommender_type.value})\n"
                    f"Relationship: {rec_input.relationship}\n"
                    f"Resume excerpt:\n{rec_input.resume_text[:1500]}\n"
                    f"Transcript excerpt:\n{rec_input.transcript_text[:1500]}"
                ),
            )
            draft_body = str(data.get("draft_body", ""))
            if DRAFT_REVIEW_BANNER not in draft_body:
                draft_body = f"{DRAFT_REVIEW_BANNER}\n{draft_body}"
            return RecommendationGenerationOutput(
                draft_body=draft_body,
                key_talking_points=[str(item) for item in data.get("key_talking_points", [])],
                why_it_matches=str(data.get("why_it_matches", "")),
                generation_method="openai",
            )
        except Exception:
            result = fallback.generate(rec_input)
            result.generation_method = "deterministic_fallback"
            return result
