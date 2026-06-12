from datetime import datetime, timezone

from pydantic import Field

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import APIModel, AgentActionLog, AgentActionStatus, RecommendationDraft, RecommendationStatus
from app.models.recommendation_draft import RecommenderType
from app.services.application_service import build_application_bundle
from app.services.recommendation_service import (
    generate_recommendation_draft,
    next_draft_version,
    resolve_recommender,
)


class GenerateRecommendationRequest(APIModel):
    recommender_type: RecommenderType = RecommenderType.PROFESSOR
    recommender_name: str | None = None
    recommender_email: str | None = None


class RecommendationGenerateResult(APIModel):
    recommendation_draft: RecommendationDraft
    key_talking_points: list[str] = Field(default_factory=list)
    why_it_matches: str = ""


class RecommendationAgent(BaseAgent):
    """Generates scholarship-specific recommendation drafts for recommender review."""

    name = "recommendation-agent"

    def __init__(
        self,
        repository: GrantPilotRepository,
        generation_method: str = "deterministic",
    ):
        self.repository = repository
        self.generation_method = generation_method

    async def run(self, context: AgentContext) -> AgentResult:
        if not context.application_id:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                summary="application_id is required in AgentContext",
            )
        recommender_type = RecommenderType(
            str(context.metadata.get("recommender_type", RecommenderType.PROFESSOR.value))
        )
        result = await self.generate_for_application(
            context.application_id,
            GenerateRecommendationRequest(recommender_type=recommender_type),
            context.user_id,
        )
        return AgentResult(
            agent_name=self.name,
            status="completed",
            summary=f"Generated recommendation draft v{result.recommendation_draft.version_number}.",
            metadata={"recommendation_draft_id": result.recommendation_draft.id},
        )

    async def generate_for_application(
        self,
        application_id: str,
        request: GenerateRecommendationRequest | None = None,
        user_id: str = DEFAULT_USER_ID,
    ) -> RecommendationGenerateResult:
        request = request or GenerateRecommendationRequest()
        action_id = f"agent_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        action_log = AgentActionLog(
            id=action_id,
            user_id=user_id,
            agent_name=self.name,
            action_type="generate_recommendation",
            status=AgentActionStatus.STARTED,
            input_summary=f"Drafting recommendation for application {application_id}",
            metadata={
                "application_id": application_id,
                "recommender_type": request.recommender_type.value,
                "generation_method": self.generation_method,
            },
        )
        self.repository.create_record(action_log)

        bundle = build_application_bundle(self.repository, application_id)
        profile = self.repository.get_user_profile(user_id)
        documents = self.repository.list_documents(user_id)
        existing_drafts = sorted(bundle.recommendation_drafts, key=lambda item: item.version_number)

        name, email, relationship = resolve_recommender(
            request.recommender_type,
            existing_drafts,
            request.recommender_name,
            request.recommender_email,
        )

        output = generate_recommendation_draft(
            profile=profile,
            opportunity=bundle.opportunity,
            documents=documents,
            recommender_type=request.recommender_type,
            recommender_name=name,
            relationship=relationship,
            method=self.generation_method,
        )

        version_number = next_draft_version(existing_drafts)
        source_draft = existing_drafts[-1] if existing_drafts else None
        draft_id = (
            f"rec_{application_id}_v{version_number}_"
            f"{datetime.now(timezone.utc).strftime('%H%M%S')}"
        )

        recommendation_draft = RecommendationDraft(
            id=draft_id,
            application_id=application_id,
            recommender_name=name,
            recommender_email=email,
            relationship=relationship,
            recommender_type=request.recommender_type,
            draft_body=output.draft_body,
            version_number=version_number,
            source_draft_id=source_draft.id if source_draft else None,
            key_talking_points=output.key_talking_points,
            why_it_matches=output.why_it_matches,
            status=RecommendationStatus.DRAFTED,
            metadata={
                "agent": self.name,
                "generation_method": output.generation_method,
                "opportunity_id": bundle.opportunity.id,
                "draft_for_recommender_review": True,
            },
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.repository.create_record(recommendation_draft)

        self.repository.update_record(
            AgentActionLog,
            action_id,
            {
                "status": AgentActionStatus.COMPLETED,
                "output_summary": f"Created recommendation draft v{version_number} for {name}.",
                "metadata": {
                    "application_id": application_id,
                    "recommendation_draft_id": recommendation_draft.id,
                    "version_number": version_number,
                },
            },
        )

        return RecommendationGenerateResult(
            recommendation_draft=recommendation_draft,
            key_talking_points=output.key_talking_points,
            why_it_matches=output.why_it_matches,
        )
