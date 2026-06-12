from abc import ABC, abstractmethod

from pydantic import Field

from app.models import APIModel, Opportunity, UploadedDocument, UserProfile


class EssayGenerationInput(APIModel):
    profile: UserProfile
    opportunity: Opportunity
    original_essay: str
    prompt: str
    prior_version_content: str | None = None


class EssayGenerationOutput(APIModel):
    revised_essay: str
    improvement_suggestions: list[str] = Field(default_factory=list)
    change_summary: str = ""
    generation_method: str = "deterministic"


class EssayGenerator(ABC):
    """Essay generation backend — swap in LLM generation later."""

    @abstractmethod
    def generate(self, essay_input: EssayGenerationInput) -> EssayGenerationOutput:
        raise NotImplementedError
