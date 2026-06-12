from abc import ABC, abstractmethod

from pydantic import Field

from app.models import APIModel, Opportunity, RecommenderType, UploadedDocument, UserProfile


class RecommendationGenerationInput(APIModel):
    profile: UserProfile
    opportunity: Opportunity
    recommender_type: RecommenderType
    recommender_name: str
    relationship: str
    resume_text: str = ""
    transcript_text: str = ""
    existing_letters: list[str] = Field(default_factory=list)


class RecommendationGenerationOutput(APIModel):
    draft_body: str
    key_talking_points: list[str] = Field(default_factory=list)
    why_it_matches: str = ""
    generation_method: str = "deterministic"


class RecommendationGenerator(ABC):
    """Recommendation draft backend — swap in LLM generation later."""

    @abstractmethod
    def generate(self, rec_input: RecommendationGenerationInput) -> RecommendationGenerationOutput:
        raise NotImplementedError
