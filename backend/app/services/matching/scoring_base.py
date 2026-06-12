from abc import ABC, abstractmethod

from pydantic import Field

from app.models import APIModel, MatchPriority, Opportunity, UploadedDocument, UserProfile


class MatchScoreInput(APIModel):
    profile: UserProfile
    opportunity: Opportunity
    resume: UploadedDocument | None = None
    transcript: UploadedDocument | None = None
    personal_essay: UploadedDocument | None = None
    recommendation_letters: list[UploadedDocument] = Field(default_factory=list)


class MatchScoreOutput(APIModel):
    score: float = Field(ge=0, le=1)
    score_percent: int = Field(ge=0, le=100)
    priority: MatchPriority
    rationale: str
    fit_explanation: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    missing_materials: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    funding_potential: str = ""
    success_probability: float = Field(ge=0, le=1, default=0)
    scoring_method: str = "deterministic"


class MatchScorer(ABC):
    """Scoring backend abstraction — swap in AI scoring later."""

    @abstractmethod
    def score(self, match_input: MatchScoreInput) -> MatchScoreOutput:
        raise NotImplementedError
