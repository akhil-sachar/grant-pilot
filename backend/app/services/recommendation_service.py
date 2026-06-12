from app.models import DocumentType, Opportunity, RecommenderType, UploadedDocument, UserProfile
from app.models.recommendation_draft import RecommendationDraft
from app.services.recommendation.deterministic_generator import (
    AIRecommendationGenerator,
    DeterministicRecommendationGenerator,
)
from app.services.recommendation.generator_base import (
    RecommendationGenerationInput,
    RecommendationGenerationOutput,
    RecommendationGenerator,
)

_DEFAULT_RECOMMENDERS: dict[RecommenderType, tuple[str, str, str]] = {
    RecommenderType.PROFESSOR: ("Dr. Ana Patel", "apatel@example.edu", "Faculty research mentor"),
    RecommenderType.ADVISOR: ("Jordan Lee", "jlee@example.edu", "Academic advisor"),
    RecommenderType.MENTOR: ("Sam Rivera", "sam.rivera@example.org", "Civic tech mentor"),
    RecommenderType.MANAGER: ("Taylor Brooks", "tbrooks@example.com", "Project supervisor"),
}


def get_recommendation_generator(method: str = "deterministic") -> RecommendationGenerator:
    if method in {"ai", "openai"}:
        return AIRecommendationGenerator()
    return DeterministicRecommendationGenerator()


def resolve_recommender(
    recommender_type: RecommenderType,
    existing_drafts: list[RecommendationDraft],
    name: str | None = None,
    email: str | None = None,
) -> tuple[str, str, str]:
    if name and email:
        default = _DEFAULT_RECOMMENDERS[recommender_type]
        return name, email, default[2]

    for draft in existing_drafts:
        if draft.recommender_type == recommender_type:
            return draft.recommender_name, str(draft.recommender_email), draft.relationship

    return _DEFAULT_RECOMMENDERS[recommender_type]


def collect_document_text(documents: list[UploadedDocument], doc_type: DocumentType) -> str:
    matches = [doc for doc in documents if doc.document_type == doc_type]
    if not matches:
        return ""
    latest = sorted(matches, key=lambda doc: doc.updated_at, reverse=True)[0]
    return latest.extracted_text or latest.extracted_text_preview or ""


def collect_existing_letters(documents: list[UploadedDocument]) -> list[str]:
    letters = []
    for document in documents:
        if document.document_type != DocumentType.RECOMMENDATION:
            continue
        text = document.extracted_text or document.extracted_text_preview
        if text:
            letters.append(text)
    return letters


def generate_recommendation_draft(
    profile: UserProfile,
    opportunity: Opportunity,
    documents: list[UploadedDocument],
    recommender_type: RecommenderType,
    recommender_name: str,
    relationship: str,
    method: str = "deterministic",
) -> RecommendationGenerationOutput:
    generator = get_recommendation_generator(method)
    rec_input = RecommendationGenerationInput(
        profile=profile,
        opportunity=opportunity,
        recommender_type=recommender_type,
        recommender_name=recommender_name,
        relationship=relationship,
        resume_text=collect_document_text(documents, DocumentType.RESUME),
        transcript_text=collect_document_text(documents, DocumentType.TRANSCRIPT),
        existing_letters=collect_existing_letters(documents),
    )
    return generator.generate(rec_input)


def next_draft_version(existing_drafts: list[RecommendationDraft]) -> int:
    if not existing_drafts:
        return 1
    return max(draft.version_number for draft in existing_drafts) + 1
