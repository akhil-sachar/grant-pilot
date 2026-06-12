from datetime import datetime, timezone

from pydantic import Field

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import APIModel, AgentActionStatus, EmailType, OutreachEmail, OutreachEmailStatus, RecipientRole
from app.services.agent_run_tracker import get_agent_run_tracker
from app.services.application_service import build_application_bundle
from app.services.composio_service import ComposioActionResult, ComposioService, get_composio_service
from app.services.outreach_service import generate_outreach_email, next_email_version, resolve_recipient


class GenerateOutreachRequest(APIModel):
    recipient_role: RecipientRole = RecipientRole.PROFESSOR
    email_type: EmailType = EmailType.RECOMMENDATION_REQUEST
    recipient_name: str | None = None
    recipient_email: str | None = None
    run_composio_actions: bool = True


class OutreachGenerateResult(APIModel):
    outreach_email: OutreachEmail
    suggested_follow_up: str
    composio_mode: str
    composio_actions: list[ComposioActionResult] = Field(default_factory=list)


class OutreachAgent(BaseAgent):
    """Generates personalized outreach emails and orchestrates Composio workflows."""

    name = "outreach-agent"

    def __init__(
        self,
        repository: GrantPilotRepository,
        composio: ComposioService | None = None,
        generation_method: str = "deterministic",
    ):
        self.repository = repository
        self.composio = composio or get_composio_service(repository)
        self.generation_method = generation_method

    async def run(self, context: AgentContext) -> AgentResult:
        if not context.application_id:
            return AgentResult(
                agent_name=self.name,
                status="failed",
                summary="application_id is required in AgentContext",
            )
        result = await self.generate_for_application(
            context.application_id,
            GenerateOutreachRequest(),
            context.user_id,
        )
        return AgentResult(
            agent_name=self.name,
            status="completed",
            summary=f"Generated outreach email: {result.outreach_email.subject}",
            metadata={"outreach_email_id": result.outreach_email.id},
        )

    async def generate_for_application(
        self,
        application_id: str,
        request: GenerateOutreachRequest | None = None,
        user_id: str = DEFAULT_USER_ID,
    ) -> OutreachGenerateResult:
        request = request or GenerateOutreachRequest()
        tracker = get_agent_run_tracker(self.repository)
        action_id = tracker.start(
            user_id,
            self.name,
            "generate_outreach",
            f"Outreach for application {application_id}",
            metadata={
                "application_id": application_id,
                "recipient_role": request.recipient_role.value,
                "email_type": request.email_type.value,
                "composio_mode": self.composio.mode.value,
            },
        )

        try:
            bundle = build_application_bundle(self.repository, application_id)
            profile = self.repository.get_user_profile(user_id)
            name, email = resolve_recipient(
                request.recipient_role,
                request.recipient_name,
                request.recipient_email,
            )

            output = generate_outreach_email(
                profile=profile,
                opportunity=bundle.opportunity,
                recipient_role=request.recipient_role,
                email_type=request.email_type,
                recipient_name=name,
                recipient_email=email,
                method=self.generation_method,
            )

            version_number = next_email_version(bundle.outreach_emails)
            source_email = bundle.outreach_emails[-1] if bundle.outreach_emails else None
            email_id = f"email_{application_id}_v{version_number}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

            outreach_email = OutreachEmail(
                id=email_id,
                application_id=application_id,
                recipient_email=email,
                recipient_role=request.recipient_role,
                email_type=request.email_type,
                subject=output.subject,
                body=output.body,
                suggested_follow_up=output.suggested_follow_up,
                version_number=version_number,
                source_email_id=source_email.id if source_email else None,
                status=OutreachEmailStatus.DRAFT,
                metadata={
                    "agent": self.name,
                    "generation_method": output.generation_method,
                    "recipient_name": name,
                    "opportunity_id": bundle.opportunity.id,
                    "composio_mode": self.composio.mode.value,
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.repository.create_record(outreach_email)

            composio_actions: list[ComposioActionResult] = []
            if request.run_composio_actions:
                composio_actions = await self.composio.run_outreach_workflow(
                    user_id=user_id,
                    to=email,
                    subject=output.subject,
                    body=output.body,
                    follow_up=output.suggested_follow_up,
                    doc_title=f"{bundle.opportunity.title} — Outreach Draft",
                )

            tracker.finish(
                action_id,
                status=AgentActionStatus.COMPLETED,
                output_summary=f"Created outreach email v{version_number} and ran {len(composio_actions)} Composio actions.",
                metadata={
                    "application_id": application_id,
                    "outreach_email_id": outreach_email.id,
                    "composio_actions": [action.model_dump(mode="json") for action in composio_actions],
                    "actions": len(composio_actions),
                },
            )

            return OutreachGenerateResult(
                outreach_email=outreach_email,
                suggested_follow_up=output.suggested_follow_up,
                composio_mode=self.composio.mode.value,
                composio_actions=composio_actions,
            )
        except Exception as exc:
            tracker.finish(
                action_id,
                status=AgentActionStatus.FAILED,
                output_summary=str(exc),
                metadata={"application_id": application_id},
            )
            raise
