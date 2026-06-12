from datetime import datetime, timezone

from pydantic import Field

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import APIModel, AgentActionStatus, EssayStatus, EssayVersion
from app.services.agent_run_tracker import get_agent_run_tracker
from app.services.application_service import build_application_bundle
from app.services.essay_service import (
    build_essay_prompt,
    generate_opportunity_essay,
    resolve_original_essay,
)


class EssayImproveResult(APIModel):
    essay_version: EssayVersion
    original_essay: str
    improvement_suggestions: list[str] = Field(default_factory=list)
    change_summary: str = ""


class EssayAgent(BaseAgent):
    """Generates scholarship-specific essay versions without overwriting originals."""

    name = "essay-agent"

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
        result = await self.improve_for_application(context.application_id, context.user_id)
        return AgentResult(
            agent_name=self.name,
            status="completed",
            summary=result.change_summary,
            metadata={"essay_version_id": result.essay_version.id},
        )

    async def improve_for_application(
        self,
        application_id: str,
        user_id: str = DEFAULT_USER_ID,
    ) -> EssayImproveResult:
        tracker = get_agent_run_tracker(self.repository)
        action_id = tracker.start(
            user_id,
            self.name,
            "improve_essay",
            f"Tailoring essay for application {application_id}",
            metadata={"application_id": application_id, "generation_method": self.generation_method},
        )

        try:
            bundle = build_application_bundle(self.repository, application_id)
            profile = self.repository.get_user_profile(user_id)
            documents = self.repository.list_documents(user_id)
            essay_versions = sorted(bundle.essay_versions, key=lambda item: item.version_number)

            original_text, source_ref = resolve_original_essay(documents, essay_versions)
            if not original_text:
                raise ValueError("No personal essay found. Upload a personal essay in Documents first.")

            if not essay_versions:
                baseline = EssayVersion(
                    id=f"essay_{application_id}_v1",
                    application_id=application_id,
                    prompt=build_essay_prompt(bundle.opportunity),
                    content=original_text,
                    version_number=1,
                    status=EssayStatus.DRAFT,
                    feedback_notes=["Original essay preserved as baseline version."],
                    metadata={
                        "is_original": True,
                        "source_document_id": source_ref,
                        "agent": self.name,
                    },
                )
                self.repository.create_record(baseline)
                essay_versions = [baseline]

            original_version = next(
                (version for version in essay_versions if version.metadata.get("is_original")),
                essay_versions[0],
            )
            latest = essay_versions[-1]
            next_version_number = latest.version_number + 1
            prompt = build_essay_prompt(bundle.opportunity)

            output = generate_opportunity_essay(
                profile=profile,
                opportunity=bundle.opportunity,
                original_essay=original_version.content,
                prompt=prompt,
                method=self.generation_method,
                prior_version_content=latest.content,
            )

            essay_id = f"essay_{application_id}_v{next_version_number}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
            essay_version = EssayVersion(
                id=essay_id,
                application_id=application_id,
                prompt=prompt,
                content=output.revised_essay,
                version_number=next_version_number,
                status=EssayStatus.REVIEW,
                feedback_notes=output.improvement_suggestions,
                source_version_id=latest.id,
                change_summary=output.change_summary,
                metadata={
                    "agent": self.name,
                    "generation_method": output.generation_method,
                    "opportunity_id": bundle.opportunity.id,
                    "source_version_id": latest.id,
                    "original_version_id": original_version.id,
                },
            )
            self.repository.create_record(essay_version)

            tracker.finish(
                action_id,
                status=AgentActionStatus.COMPLETED,
                output_summary=output.change_summary,
                metadata={
                    "application_id": application_id,
                    "essay_version_id": essay_version.id,
                    "version_number": next_version_number,
                },
            )

            return EssayImproveResult(
                essay_version=essay_version,
                original_essay=original_version.content,
                improvement_suggestions=output.improvement_suggestions,
                change_summary=output.change_summary,
            )
        except Exception as exc:
            tracker.finish(
                action_id,
                status=AgentActionStatus.FAILED,
                output_summary=str(exc),
                metadata={"application_id": application_id},
            )
            raise
