from app.models import DocumentType, Opportunity, UploadedDocument, UserProfile
from app.services.matching.deterministic_scorer import AIMatchScorer, DeterministicMatchScorer
from app.services.matching.scoring_base import MatchScoreInput, MatchScoreOutput, MatchScorer


def build_match_input(
    profile: UserProfile,
    opportunity: Opportunity,
    documents: list[UploadedDocument],
) -> MatchScoreInput:
    by_type: dict[DocumentType, list[UploadedDocument]] = {}
    for document in documents:
        by_type.setdefault(document.document_type, []).append(document)

    return MatchScoreInput(
        profile=profile,
        opportunity=opportunity,
        resume=_latest(by_type.get(DocumentType.RESUME)),
        transcript=_latest(by_type.get(DocumentType.TRANSCRIPT)),
        personal_essay=_latest(by_type.get(DocumentType.ESSAY)),
        recommendation_letters=by_type.get(DocumentType.RECOMMENDATION, []),
    )


def get_match_scorer(method: str = "deterministic") -> MatchScorer:
    if method == "ai":
        return AIMatchScorer()
    return DeterministicMatchScorer()


def score_opportunity(
    profile: UserProfile,
    opportunity: Opportunity,
    documents: list[UploadedDocument],
    method: str = "deterministic",
) -> MatchScoreOutput:
    scorer = get_match_scorer(method)
    match_input = build_match_input(profile, opportunity, documents)
    return scorer.score(match_input)


def _latest(documents: list[UploadedDocument] | None) -> UploadedDocument | None:
    if not documents:
        return None
    return sorted(documents, key=lambda doc: doc.updated_at, reverse=True)[0]
