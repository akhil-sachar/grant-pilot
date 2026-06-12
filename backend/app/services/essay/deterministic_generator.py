from app.models import Opportunity, UserProfile
from app.services.essay.generator_base import EssayGenerationInput, EssayGenerationOutput, EssayGenerator


class DeterministicEssayGenerator(EssayGenerator):
    """Rule-based essay tailoring using opportunity and profile context."""

    def generate(self, essay_input: EssayGenerationInput) -> EssayGenerationOutput:
        profile = essay_input.profile
        opportunity = essay_input.opportunity
        original = essay_input.original_essay.strip()
        themes = self._opportunity_themes(opportunity)
        profile_hooks = self._profile_hooks(profile, opportunity)

        opening = (
            f"When I learned about {opportunity.title} from {opportunity.provider_name}, "
            f"I saw a direct connection to my work in {profile.major or 'my field'}: "
            f"{themes[0] if themes else 'creating meaningful public impact'}."
        )

        alignment = (
            f"This opportunity aligns with my goal to {profile.career_goals[0].lower() if profile.career_goals else 'serve my community'}. "
            f"Through {profile.projects[0] if profile.projects else 'hands-on project work'}, "
            f"I have already begun addressing {themes[1] if len(themes) > 1 else 'real community needs'}."
        )

        revised_body = original
        if original.lower().startswith("draft outline"):
            revised_body = (
                f"{opening}\n\n"
                f"{alignment}\n\n"
                f"Community problem: neighbors struggled to find timely information about local assistance programs.\n"
                f"Prototype response: I built tools that translate public data into accessible civic services.\n"
                f"Measurable outcome: early users reported faster access to benefits navigation and clearer next steps.\n"
                f"Future plan: expand the work with mentorship, stronger evaluation, and broader community partnerships."
            )
        else:
            revised_body = f"{opening}\n\n{original}\n\n{alignment}"

        closing = (
            f"Award support from {opportunity.provider_name} would help me deepen this work, "
            f"complete {opportunity.title.lower()}, and deliver outcomes that match the program's focus on "
            f"{opportunity.eligibility_summary.rstrip('.').lower()}."
        )
        revised_essay = f"{revised_body}\n\n{closing}".strip()

        suggestions = [
            f"Lead with a concrete story tied to {opportunity.provider_name}'s mission.",
            f"Name one measurable outcome from {profile.projects[0] if profile.projects else 'your project'}.",
            "Tighten the closing paragraph to mirror the opportunity's evaluation criteria.",
            f"Reference at least two themes from the prompt: {', '.join(themes[:3])}.",
        ]
        if "portfolio" in " ".join(opportunity.requirements).lower():
            suggestions.append("Add a sentence pointing reviewers to your portfolio or prototype link.")

        change_summary = (
            f"Added opportunity-specific opening and closing tailored to {opportunity.title}; "
            f"integrated profile themes ({', '.join(profile_hooks[:2])}) and preserved the original narrative core."
        )

        return EssayGenerationOutput(
            revised_essay=revised_essay,
            improvement_suggestions=suggestions,
            change_summary=change_summary,
            generation_method="deterministic",
        )

    def _opportunity_themes(self, opportunity: Opportunity) -> list[str]:
        themes = list(opportunity.tags)
        for phrase in opportunity.description.split("."):
            cleaned = phrase.strip()
            if len(cleaned) > 12:
                themes.append(cleaned[:80])
            if len(themes) >= 4:
                break
        return themes or [opportunity.opportunity_type.value.replace("_", " ")]

    def _profile_hooks(self, profile: UserProfile, opportunity: Opportunity) -> list[str]:
        hooks: list[str] = []
        if profile.major:
            hooks.append(profile.major)
        hooks.extend(profile.career_goals[:2])
        hooks.extend(profile.research_interests[:1])
        for tag in opportunity.tags:
            if any(tag.lower() in value.lower() for value in hooks):
                continue
            hooks.append(tag)
        return hooks[:4]


class AIEssayGenerator(EssayGenerator):
    """Placeholder for future LLM-based essay generation."""

    def generate(self, essay_input: EssayGenerationInput) -> EssayGenerationOutput:
        raise NotImplementedError("AI essay generation is not enabled yet.")
