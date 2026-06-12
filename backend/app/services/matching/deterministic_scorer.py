from __future__ import annotations

import re
from datetime import date, datetime, timezone

from app.models import DocumentProcessingStatus, DocumentType, MatchPriority, Opportunity
from app.services.llm.context import document_summary, opportunity_summary, profile_summary
from app.services.matching.scoring_base import MatchScoreInput, MatchScoreOutput, MatchScorer

_REQUIREMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "resume": ("resume", "cv"),
    "transcript": ("transcript",),
    "personal statement": ("personal statement", "statement", "essay"),
    "essay": ("essay", "statement"),
    "recommendation": ("recommendation", "reference", "letter"),
    "portfolio": ("portfolio", "project"),
    "budget": ("budget",),
    "financial": ("financial", "fafsa", "need"),
    "faculty": ("faculty", "mentor", "sponsor"),
}

_PROFILE_KEYWORDS = (
    "first-generation",
    "first generation",
    "undergraduate",
    "graduate",
    "stem",
    "research",
    "civic",
    "public",
    "ai",
    "data",
    "nonprofit",
    "startup",
    "community college",
    "transfer",
)


class DeterministicMatchScorer(MatchScorer):
    """Rule-based scorer using profile fields and uploaded document readiness."""

    def score(self, match_input: MatchScoreInput) -> MatchScoreOutput:
        profile = match_input.profile
        opportunity = match_input.opportunity

        profile_text = self._profile_corpus(profile)
        opportunity_text = self._opportunity_corpus(opportunity)

        profile_fit = self._score_profile_fit(profile, profile_text, opportunity, opportunity_text)
        doc_readiness, missing, doc_strengths, doc_gaps = self._score_documents(
            match_input, opportunity
        )
        academic = self._score_academic(profile, opportunity_text)
        urgency = self._score_deadline_urgency(opportunity.deadline)

        raw_total = profile_fit + doc_readiness + academic + urgency
        score_percent = max(0, min(100, round(raw_total)))
        score = round(score_percent / 100, 4)
        priority = self._priority_for(score_percent)

        keyword_strengths = self._keyword_strengths(profile_text, opportunity_text)
        strengths = keyword_strengths + doc_strengths
        gaps = doc_gaps
        if profile.gpa and profile.gpa < 3.5 and "scholarship" in opportunity_text:
            gaps.append("GPA is below typical merit scholarship threshold")

        recommended_actions = self._recommended_actions(missing, gaps, opportunity)
        fit_explanation = self._fit_explanation(profile, opportunity, keyword_strengths, score_percent)
        rationale = fit_explanation
        funding_potential = self._funding_potential(opportunity, score_percent, priority)
        readiness_ratio = doc_readiness / 35 if doc_readiness else 0
        success_probability = round(
            min(1.0, (score_percent / 100) * (0.6 + 0.4 * readiness_ratio) * self._urgency_factor(opportunity.deadline)),
            4,
        )

        return MatchScoreOutput(
            score=score,
            score_percent=score_percent,
            priority=priority,
            rationale=rationale,
            fit_explanation=fit_explanation,
            strengths=strengths[:6],
            gaps=gaps[:5],
            missing_materials=missing,
            recommended_actions=recommended_actions[:5],
            funding_potential=funding_potential,
            success_probability=success_probability,
            scoring_method="deterministic",
        )

    def _score_profile_fit(
        self,
        profile,
        profile_text: str,
        opportunity: Opportunity,
        opportunity_text: str,
    ) -> float:
        points = 0.0
        overlap = self._token_overlap(profile_text, opportunity_text)
        points += min(20, overlap * 4)

        for tag in opportunity.tags:
            if tag.lower() in profile_text:
                points += 2

        demo = profile.demographic_info or {}
        if demo.get("first_generation") and any(
            term in opportunity_text for term in ("first-generation", "first generation", "first gen")
        ):
            points += 8

        if profile.major and profile.major.lower() in opportunity_text:
            points += 4

        for goal in profile.career_goals + profile.research_interests + profile.funding_goals:
            if goal.lower() in opportunity_text:
                points += 2

        if profile.education_level and "undergraduate" in profile.education_level.lower():
            if "undergraduate" in opportunity_text or opportunity.opportunity_type.value == "scholarship":
                points += 4

        return min(40, points)

    def _score_documents(
        self,
        match_input: MatchScoreInput,
        opportunity: Opportunity,
    ) -> tuple[float, list[str], list[str], list[str]]:
        required = opportunity.requirements or []
        if not required:
            required = ["Resume", "Transcript", "Personal statement"]

        present_labels: set[str] = set()
        strengths: list[str] = []
        gaps: list[str] = []
        missing: list[str] = []

        doc_map = {
            "resume": match_input.resume,
            "transcript": match_input.transcript,
            "personal statement": match_input.personal_essay,
            "essay": match_input.personal_essay,
        }

        for label, document in doc_map.items():
            if document and self._document_ready(document):
                present_labels.add(label)
                strengths.append(f"{label.title()} on file")

        if match_input.recommendation_letters:
            ready_count = sum(1 for doc in match_input.recommendation_letters if self._document_ready(doc))
            if ready_count:
                present_labels.add("recommendation")
                strengths.append(f"{ready_count} recommendation letter(s) uploaded")

        matched_requirements = 0
        for requirement in required:
            req_lower = requirement.lower()
            if self._requirement_satisfied(req_lower, present_labels, match_input):
                matched_requirements += 1
            else:
                missing.append(requirement)
                gaps.append(f"Missing: {requirement}")

        ratio = matched_requirements / len(required) if required else 1
        points = round(35 * ratio, 1)
        return points, missing, strengths, gaps

    def _score_academic(self, profile, opportunity_text: str) -> float:
        if profile.gpa is None:
            return 5.0
        if profile.gpa >= 3.8:
            base = 15.0
        elif profile.gpa >= 3.5:
            base = 12.0
        elif profile.gpa >= 3.0:
            base = 8.0
        else:
            base = 4.0
        if "merit" in opportunity_text and profile.gpa < 3.5:
            base *= 0.7
        return base

    def _score_deadline_urgency(self, deadline: date | None) -> float:
        if deadline is None:
            return 6.0
        days = (deadline - datetime.now(timezone.utc).date()).days
        if days < 0:
            return 0.0
        if days >= 60:
            return 10.0
        if days >= 30:
            return 8.0
        if days >= 14:
            return 6.0
        return 3.0

    def _urgency_factor(self, deadline: date | None) -> float:
        if deadline is None:
            return 0.95
        days = (deadline - datetime.now(timezone.utc).date()).days
        if days < 0:
            return 0.2
        if days < 14:
            return 0.75
        if days < 30:
            return 0.88
        return 1.0

    def _priority_for(self, score_percent: int) -> MatchPriority:
        if score_percent >= 75:
            return MatchPriority.HIGH
        if score_percent >= 50:
            return MatchPriority.MEDIUM
        return MatchPriority.LOW

    def _funding_potential(self, opportunity: Opportunity, score_percent: int, priority: MatchPriority) -> str:
        amount_label = self._format_amount(opportunity)
        tier = priority.value.capitalize()
        if score_percent >= 75:
            return f"{tier} — strong fit for {amount_label}"
        if score_percent >= 50:
            return f"{tier} — competitive for {amount_label}"
        return f"{tier} — stretch opportunity ({amount_label})"

    def _format_amount(self, opportunity: Opportunity) -> str:
        if opportunity.amount_min and opportunity.amount_max and opportunity.amount_min != opportunity.amount_max:
            low = f"${opportunity.amount_min:,}"
            high = f"${opportunity.amount_max:,}"
            return f"{low}–{high}"
        if opportunity.amount_max:
            return f"up to ${opportunity.amount_max:,}"
        if opportunity.amount_min:
            return f"from ${opportunity.amount_min:,}"
        return "variable funding"

    def _fit_explanation(
        self,
        profile,
        opportunity: Opportunity,
        keyword_strengths: list[str],
        score_percent: int,
    ) -> str:
        themes = ", ".join(keyword_strengths[:3]) if keyword_strengths else "general profile alignment"
        return (
            f"{profile.full_name}'s background in {profile.major or 'their field'} aligns with "
            f"{opportunity.title} ({score_percent}/100). Strongest signals: {themes}."
        )

    def _recommended_actions(
        self,
        missing: list[str],
        gaps: list[str],
        opportunity: Opportunity,
    ) -> list[str]:
        actions: list[str] = []
        for item in missing[:3]:
            actions.append(f"Upload or complete: {item}")
        if not missing and opportunity.deadline:
            actions.append(f"Begin application before {opportunity.deadline.isoformat()}")
        if gaps and not missing:
            actions.append("Address material gaps noted in the fit review")
        if not actions:
            actions.append("Review requirements and start the application checklist")
        return actions

    def _keyword_strengths(self, profile_text: str, opportunity_text: str) -> list[str]:
        strengths: list[str] = []
        for keyword in _PROFILE_KEYWORDS:
            if keyword in profile_text and keyword in opportunity_text:
                strengths.append(f"Shared focus on {keyword}")
        for interest in re.findall(r"[a-z]{4,}", profile_text):
            if interest in opportunity_text and interest not in strengths:
                if len(strengths) >= 4:
                    break
        return strengths

    def _profile_corpus(self, profile) -> str:
        parts = [
            profile.major or "",
            profile.education_level or "",
            profile.school_name or "",
            " ".join(profile.fields_of_study),
            " ".join(profile.career_goals),
            " ".join(profile.research_interests),
            " ".join(profile.projects),
            " ".join(profile.awards),
            " ".join(profile.funding_goals),
        ]
        demo = profile.demographic_info or {}
        if demo.get("first_generation"):
            parts.append("first-generation first generation first gen")
        return " ".join(parts).lower()

    def _opportunity_corpus(self, opportunity: Opportunity) -> str:
        return " ".join(
            [
                opportunity.title,
                opportunity.description,
                opportunity.eligibility_summary,
                " ".join(opportunity.tags),
                " ".join(opportunity.requirements),
                opportunity.opportunity_type.value,
            ]
        ).lower()

    def _token_overlap(self, left: str, right: str) -> int:
        left_tokens = set(re.findall(r"[a-z]{4,}", left))
        right_tokens = set(re.findall(r"[a-z]{4,}", right))
        stop = {"with", "that", "this", "from", "your", "have", "will", "students", "program"}
        return len((left_tokens & right_tokens) - stop)

    def _document_ready(self, document) -> bool:
        return document.status in {
            DocumentProcessingStatus.PROCESSED,
            DocumentProcessingStatus.NEEDS_REVIEW,
            DocumentProcessingStatus.UPLOADED,
        }

    def _requirement_satisfied(
        self,
        requirement: str,
        present_labels: set[str],
        match_input: MatchScoreInput,
    ) -> bool:
        for label, keywords in _REQUIREMENT_KEYWORDS.items():
            if any(keyword in requirement for keyword in keywords):
                if label in present_labels:
                    return True
                if label == "recommendation" and match_input.recommendation_letters:
                    return any(self._document_ready(doc) for doc in match_input.recommendation_letters)
        if "portfolio" in requirement and match_input.profile.projects:
            return True
        if "fafsa" in requirement or "financial" in requirement:
            return any(doc.document_type == DocumentType.FINANCIAL_AID for doc in [match_input.transcript])
        return False


class AIMatchScorer(MatchScorer):
    """OpenAI-powered opportunity matching with Langfuse tracing."""

    def score(self, match_input: MatchScoreInput) -> MatchScoreOutput:
        from app.services.llm.openai_service import get_openai_service

        llm = get_openai_service()
        fallback = DeterministicMatchScorer()
        try:
            data = llm.chat_json(
                agent_name="matching-agent",
                action="score_opportunity",
                system_prompt=(
                    "You score scholarship/grant fit for a student. "
                    "Return JSON with: score_percent (0-100 int), priority (low|medium|high), "
                    "rationale (string), fit_explanation (string), strengths (string[]), gaps (string[]), "
                    "missing_materials (string[]), recommended_actions (string[]), "
                    "funding_potential (string), success_probability (0-1 float)."
                ),
                user_prompt=(
                    f"Profile:\n{profile_summary(match_input.profile)}\n\n"
                    f"Opportunity:\n{opportunity_summary(match_input.opportunity)}\n\n"
                    f"Documents:\n"
                    f"{document_summary(match_input.resume, 'Resume')}\n"
                    f"{document_summary(match_input.transcript, 'Transcript')}\n"
                    f"{document_summary(match_input.personal_essay, 'Essay')}\n"
                    f"Recommendations uploaded: {len(match_input.recommendation_letters)}"
                ),
            )
            score_percent = max(0, min(100, int(data.get("score_percent", 0))))
            score = round(score_percent / 100, 4)
            priority_raw = str(data.get("priority", "medium")).lower()
            priority = MatchPriority(priority_raw if priority_raw in {"low", "medium", "high"} else "medium")
            success_probability = max(0.0, min(1.0, float(data.get("success_probability", score))))
            return MatchScoreOutput(
                score=score,
                score_percent=score_percent,
                priority=priority,
                rationale=str(data.get("rationale", "")),
                fit_explanation=str(data.get("fit_explanation", data.get("rationale", ""))),
                strengths=[str(item) for item in data.get("strengths", [])][:6],
                gaps=[str(item) for item in data.get("gaps", [])][:5],
                missing_materials=[str(item) for item in data.get("missing_materials", [])],
                recommended_actions=[str(item) for item in data.get("recommended_actions", [])][:5],
                funding_potential=str(data.get("funding_potential", "")),
                success_probability=round(success_probability, 4),
                scoring_method="openai",
            )
        except Exception:
            result = fallback.score(match_input)
            result.scoring_method = "deterministic_fallback"
            return result
