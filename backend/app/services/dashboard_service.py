from datetime import datetime

from pydantic import Field

from app.db.repository import GrantPilotRepository
from app.models import (
    APIModel,
    AgentActionLog,
    Application,
    ApplicationStatus,
    MatchResult,
    Notification,
    Opportunity,
    UploadedDocument,
    UserProfile,
)


class DashboardMetrics(APIModel):
    active_matches: int
    applications_in_progress: int
    documents_uploaded: int
    unread_notifications: int
    next_deadline: datetime | None = None
    opportunities_found: int
    active_applications: int
    upcoming_deadlines: int
    average_match_score: float
    agent_actions: int
    high_priority_matches: int = 0


class RankedOpportunity(APIModel):
    opportunity: Opportunity
    match: MatchResult
    success_probability: float
    score_percent: int
    priority: str


class DashboardResponse(APIModel):
    profile: UserProfile
    metrics: DashboardMetrics
    top_matches: list[MatchResult] = Field(default_factory=list)
    ranked_opportunities: list[RankedOpportunity] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    applications: list[Application] = Field(default_factory=list)
    documents: list[UploadedDocument] = Field(default_factory=list)
    notifications: list[Notification] = Field(default_factory=list)
    recent_agent_actions: list[AgentActionLog] = Field(default_factory=list)
    storage: dict[str, object] = Field(default_factory=dict)


class DashboardAnalytics(APIModel):
    opportunities_found: int
    active_applications: int
    upcoming_deadlines: int
    match_scores: list[float] = Field(default_factory=list)
    average_match_score: float
    agent_actions: int
    storage_mode: str


def _rank_opportunities(
    matches: list[MatchResult],
    opportunities: list[Opportunity],
) -> list[RankedOpportunity]:
    opportunity_by_id = {item.id: item for item in opportunities}
    ranked: list[RankedOpportunity] = []
    for match in matches:
        opportunity = opportunity_by_id.get(match.opportunity_id)
        if opportunity is None:
            continue
        ranked.append(
            RankedOpportunity(
                opportunity=opportunity,
                match=match,
                success_probability=match.success_probability,
                score_percent=round(match.score * 100),
                priority=match.priority.value,
            )
        )
    return sorted(ranked, key=lambda item: item.success_probability, reverse=True)


def build_dashboard(storage: GrantPilotRepository) -> DashboardResponse:
    profile = storage.get_user_profile()
    matches = sorted(storage.list_matches(), key=lambda item: item.success_probability, reverse=True)
    applications = storage.list_applications()
    documents = storage.list_documents()
    opportunities = storage.list_opportunities()
    notifications = sorted(
        storage.list_notifications(),
        key=lambda item: item.created_at,
        reverse=True,
    )
    deadlines = [item.due_at for item in applications if item.due_at is not None]
    active_statuses = {
        ApplicationStatus.PLANNED.value,
        ApplicationStatus.IN_PROGRESS.value,
        ApplicationStatus.NEEDS_REVIEW.value,
        ApplicationStatus.READY_TO_SUBMIT.value,
    }
    active_applications = sum(1 for item in applications if item.status in active_statuses)
    average_match_score = (
        round(sum(item.score for item in matches) / len(matches), 4) if matches else 0
    )
    agent_actions = len(storage.list_agent_action_logs())
    high_priority = sum(1 for item in matches if item.priority.value == "high")

    return DashboardResponse(
        profile=profile,
        metrics=DashboardMetrics(
            active_matches=len(matches),
            applications_in_progress=active_applications,
            documents_uploaded=len(documents),
            unread_notifications=sum(1 for item in notifications if not item.is_read),
            next_deadline=min(deadlines) if deadlines else None,
            opportunities_found=len(opportunities),
            active_applications=active_applications,
            upcoming_deadlines=len(deadlines),
            average_match_score=average_match_score,
            agent_actions=agent_actions,
            high_priority_matches=high_priority,
        ),
        top_matches=matches[:5],
        ranked_opportunities=_rank_opportunities(matches, opportunities)[:10],
        opportunities=opportunities,
        applications=applications,
        documents=documents,
        notifications=notifications[:5],
        recent_agent_actions=storage.list_agent_action_logs()[:5],
        storage=storage.health(),
    )


def build_dashboard_analytics(storage: GrantPilotRepository) -> DashboardAnalytics:
    matches = storage.list_matches()
    applications = storage.list_applications()
    opportunities = storage.list_opportunities()
    deadlines = [item for item in applications if item.due_at is not None]
    active_statuses = {
        ApplicationStatus.PLANNED.value,
        ApplicationStatus.IN_PROGRESS.value,
        ApplicationStatus.NEEDS_REVIEW.value,
        ApplicationStatus.READY_TO_SUBMIT.value,
    }
    active_applications = sum(1 for item in applications if item.status in active_statuses)
    match_scores = [item.score for item in matches]
    average_match_score = (
        round(sum(match_scores) / len(match_scores), 4) if match_scores else 0
    )

    return DashboardAnalytics(
        opportunities_found=len(opportunities),
        active_applications=active_applications,
        upcoming_deadlines=len(deadlines),
        match_scores=match_scores,
        average_match_score=average_match_score,
        agent_actions=len(storage.list_agent_action_logs()),
        storage_mode=storage.storage_mode,
    )
