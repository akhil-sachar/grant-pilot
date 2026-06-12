from datetime import datetime, timezone

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import AgentActionLog, AgentActionStatus, MatchResult, MatchStatus
from app.services.matching_service import score_opportunity


class MatchingAgent(BaseAgent):
    """Compares user profile and documents against each funding opportunity."""

    name = "matching-agent"

    def __init__(
        self,
        repository: GrantPilotRepository,
        scoring_method: str = "deterministic",
    ):
        self.repository = repository
        self.scoring_method = scoring_method

    async def run(self, context: AgentContext) -> AgentResult:
        return await self.match_all(context.user_id)

    async def match_all(self, user_id: str = DEFAULT_USER_ID) -> AgentResult:
        action_id = f"agent_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        action_log = AgentActionLog(
            id=action_id,
            user_id=user_id,
            agent_name=self.name,
            action_type="full_match",
            status=AgentActionStatus.STARTED,
            input_summary="Scoring all opportunities against profile and documents",
            metadata={"scoring_method": self.scoring_method},
        )
        self.repository.create_record(action_log)

        profile = self.repository.get_user_profile(user_id)
        documents = self.repository.list_documents(user_id)
        opportunities = self.repository.list_opportunities()
        existing = {match.opportunity_id: match for match in self.repository.list_matches(user_id)}

        matched = 0
        high_priority = 0
        for opportunity in opportunities:
            output = score_opportunity(profile, opportunity, documents, method=self.scoring_method)
            match_id = f"match_{opportunity.id.removeprefix('opp_')}"
            prior = existing.get(opportunity.id)
            match = MatchResult(
                id=prior.id if prior else match_id,
                user_id=user_id,
                opportunity_id=opportunity.id,
                score=output.score,
                rationale=output.rationale,
                strengths=output.strengths,
                gaps=output.gaps,
                recommended_actions=output.recommended_actions,
                priority=output.priority,
                missing_materials=output.missing_materials,
                fit_explanation=output.fit_explanation,
                funding_potential=output.funding_potential,
                success_probability=output.success_probability,
                status=prior.status if prior else MatchStatus.NEW,
                metadata={
                    "scoring_method": output.scoring_method,
                    "score_percent": output.score_percent,
                },
                created_at=prior.created_at if prior else datetime.now(timezone.utc),
            )
            if prior:
                self.repository.update_record(MatchResult, match.id, match.model_dump(mode="json"))
            else:
                self.repository.create_record(match)
            matched += 1
            if output.priority.value == "high":
                high_priority += 1

        summary = f"Scored {matched} opportunities ({high_priority} high priority)."
        self.repository.update_record(
            AgentActionLog,
            action_id,
            {
                "status": AgentActionStatus.COMPLETED,
                "output_summary": summary,
                "metadata": {"matched": matched, "high_priority": high_priority},
            },
        )

        return AgentResult(
            agent_name=self.name,
            status="completed",
            summary=summary,
            metadata={"matched": matched, "high_priority": high_priority},
        )
