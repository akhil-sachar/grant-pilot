from app.models import DocumentType, EssayVersion, Opportunity, UploadedDocument, UserProfile
from app.services.essay.deterministic_generator import AIEssayGenerator, DeterministicEssayGenerator
from app.services.essay.generator_base import EssayGenerationInput, EssayGenerationOutput, EssayGenerator


def get_essay_generator(method: str = "deterministic") -> EssayGenerator:
    if method == "ai":
        return AIEssayGenerator()
    return DeterministicEssayGenerator()


def build_essay_prompt(opportunity: Opportunity) -> str:
    return (
        f"Describe how your background and work align with {opportunity.title}. "
        f"{opportunity.eligibility_summary}"
    ).strip()


def resolve_original_essay(
    documents: list[UploadedDocument],
    essay_versions: list[EssayVersion],
) -> tuple[str, str | None]:
    """Return original essay text and optional source version/document id."""
    originals = [
        version
        for version in essay_versions
        if version.metadata.get("is_original") or version.version_number == 1
    ]
    if originals:
        source = sorted(originals, key=lambda item: item.version_number)[0]
        return source.content, source.id

    essays = sorted(
        [doc for doc in documents if doc.document_type == DocumentType.ESSAY],
        key=lambda doc: doc.updated_at,
        reverse=True,
    )
    if essays:
        document = essays[0]
        text = document.extracted_text or document.extracted_text_preview or ""
        if text:
            return text, document.id

    if essay_versions:
        earliest = sorted(essay_versions, key=lambda item: item.version_number)[0]
        return earliest.content, earliest.id

    return "", None


def generate_opportunity_essay(
    profile: UserProfile,
    opportunity: Opportunity,
    original_essay: str,
    prompt: str,
    method: str = "deterministic",
    prior_version_content: str | None = None,
) -> EssayGenerationOutput:
    generator = get_essay_generator(method)
    essay_input = EssayGenerationInput(
        profile=profile,
        opportunity=opportunity,
        original_essay=original_essay,
        prompt=prompt,
        prior_version_content=prior_version_content,
    )
    return generator.generate(essay_input)
