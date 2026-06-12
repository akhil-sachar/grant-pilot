from __future__ import annotations

from datetime import datetime, timezone

from app.db.repository import GrantPilotRepository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import (
    Application,
    MatchPriority,
    Notification,
    NotificationPriority,
    NotificationType,
    Opportunity,
    RecommendationStatus,
)


def _dedupe_key(notification_type: NotificationType, entity_id: str) -> str:
    return f"{notification_type.value}:{entity_id}"


def _existing_keys(notifications: list[Notification]) -> set[str]:
    keys: set[str] = set()
    for item in notifications:
        key = item.metadata.get("dedupe_key")
        if isinstance(key, str):
            keys.add(key)
    return keys


def build_notification_candidates(
    repository: GrantPilotRepository,
    user_id: str = DEFAULT_USER_ID,
) -> list[Notification]:
    now = datetime.now(timezone.utc)
    candidates: list[Notification] = []
    existing = _existing_keys(repository.list_notifications(user_id))

    opportunities = repository.list_opportunities()
    matches = repository.list_matches(user_id)
    applications = repository.list_applications(user_id)
    documents = repository.list_documents(user_id)

    opportunity_by_id = {item.id: item for item in opportunities}
    match_by_opportunity = {item.opportunity_id: item for item in matches}

    for opportunity in opportunities:
        key = _dedupe_key(NotificationType.NEW_OPPORTUNITY, opportunity.id)
        if key not in existing and opportunity.metadata.get("source"):
            candidates.append(
                _notification(
                    user_id=user_id,
                    title="New opportunity found",
                    message=f"{opportunity.title} from {opportunity.provider_name} was added to your feed.",
                    notification_type=NotificationType.NEW_OPPORTUNITY,
                    priority=NotificationPriority.MEDIUM,
                    action_url="/opportunities",
                    dedupe_key=key,
                    metadata={"opportunity_id": opportunity.id},
                    now=now,
                )
            )

    for match in matches:
        if match.priority == MatchPriority.HIGH or match.score >= 0.75:
            key = _dedupe_key(NotificationType.HIGH_MATCH, match.opportunity_id)
            if key not in existing:
                opportunity = opportunity_by_id.get(match.opportunity_id)
                title = opportunity.title if opportunity else "High-match opportunity"
                candidates.append(
                    _notification(
                        user_id=user_id,
                        title="High match opportunity",
                        message=f"{title} scored {round(match.score * 100)}% — strong fit for your profile.",
                        notification_type=NotificationType.HIGH_MATCH,
                        priority=NotificationPriority.HIGH,
                        action_url="/opportunities",
                        dedupe_key=key,
                        metadata={"match_id": match.id, "opportunity_id": match.opportunity_id},
                        now=now,
                    )
                )

        for material in match.missing_materials:
            key = _dedupe_key(NotificationType.MISSING_DOCUMENT, f"{match.opportunity_id}:{material}")
            if key not in existing:
                candidates.append(
                    _notification(
                        user_id=user_id,
                        title="Missing document",
                        message=f"Upload or complete: {material} for a stronger application.",
                        notification_type=NotificationType.MISSING_DOCUMENT,
                        priority=NotificationPriority.HIGH,
                        action_url="/documents",
                        dedupe_key=key,
                        metadata={"match_id": match.id, "material": material},
                        now=now,
                    )
                )

    for application in applications:
        _append_deadline_notification(candidates, existing, application, opportunity_by_id, user_id, now)
        _append_application_artifact_notifications(
            candidates,
            existing,
            repository,
            application,
            opportunity_by_id,
            user_id,
            now,
        )

    if not documents:
        key = _dedupe_key(NotificationType.MISSING_DOCUMENT, "profile_documents")
        if key not in existing:
            candidates.append(
                _notification(
                    user_id=user_id,
                    title="Missing documents",
                    message="Upload your resume, transcript, and personal essay to unlock matching.",
                    notification_type=NotificationType.MISSING_DOCUMENT,
                    priority=NotificationPriority.HIGH,
                    action_url="/documents",
                    dedupe_key=key,
                    metadata={"scope": "profile"},
                    now=now,
                )
            )

    return candidates


def _append_deadline_notification(
    candidates: list[Notification],
    existing: set[str],
    application: Application,
    opportunity_by_id: dict[str, Opportunity],
    user_id: str,
    now: datetime,
) -> None:
    if application.due_at is None:
        return
    due_at = application.due_at
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)
    days = (due_at.date() - now.date()).days
    if days < 0 or days > 14:
        return
    key = _dedupe_key(NotificationType.DEADLINE_APPROACHING, application.id)
    if key in existing:
        return
    opportunity = opportunity_by_id.get(application.opportunity_id)
    priority = NotificationPriority.URGENT if days <= 7 else NotificationPriority.HIGH
    candidates.append(
        _notification(
            user_id=user_id,
            title="Deadline approaching",
            message=f"{opportunity.title if opportunity else 'Application'} is due in {days} day(s).",
            notification_type=NotificationType.DEADLINE_APPROACHING,
            priority=priority,
            action_url=f"/applications/{application.id}",
            dedupe_key=key,
            metadata={"application_id": application.id, "days_remaining": days},
            now=now,
        )
    )


def _append_application_artifact_notifications(
    candidates: list[Notification],
    existing: set[str],
    repository: GrantPilotRepository,
    application: Application,
    opportunity_by_id: dict[str, Opportunity],
    user_id: str,
    now: datetime,
) -> None:
    opportunity = opportunity_by_id.get(application.opportunity_id)
    opp_title = opportunity.title if opportunity else "your application"

    for essay in repository.list_essay_versions(application.id):
        if essay.status.value not in {"review", "draft", "final"}:
            continue
        key = _dedupe_key(NotificationType.ESSAY_READY, essay.id)
        if key in existing:
            continue
        candidates.append(
            _notification(
                user_id=user_id,
                title="Essay ready for review",
                message=f"Version {essay.version_number} for {opp_title} is ready to review.",
                notification_type=NotificationType.ESSAY_READY,
                priority=NotificationPriority.MEDIUM,
                action_url=f"/applications/{application.id}",
                dedupe_key=key,
                metadata={"essay_id": essay.id, "application_id": application.id},
                now=now,
            )
        )

    for draft in repository.list_recommendation_drafts(application.id):
        if draft.status != RecommendationStatus.DRAFTED:
            continue
        key = _dedupe_key(NotificationType.RECOMMENDATION_READY, draft.id)
        if key in existing:
            continue
        candidates.append(
            _notification(
                user_id=user_id,
                title="Recommendation draft ready",
                message=f"A draft for {draft.recommender_name} on {opp_title} is ready for recommender review.",
                notification_type=NotificationType.RECOMMENDATION_READY,
                priority=NotificationPriority.MEDIUM,
                action_url=f"/applications/{application.id}",
                dedupe_key=key,
                metadata={"recommendation_draft_id": draft.id, "application_id": application.id},
                now=now,
            )
        )

    for email in repository.list_outreach_emails(application.id):
        if email.status.value != "draft":
            continue
        key = _dedupe_key(NotificationType.EMAIL_DRAFT_READY, email.id)
        if key in existing:
            continue
        candidates.append(
            _notification(
                user_id=user_id,
                title="Email draft ready",
                message=f"Outreach draft \"{email.subject}\" for {opp_title} is ready to send.",
                notification_type=NotificationType.EMAIL_DRAFT_READY,
                priority=NotificationPriority.MEDIUM,
                action_url=f"/applications/{application.id}",
                dedupe_key=key,
                metadata={"outreach_email_id": email.id, "application_id": application.id},
                now=now,
            )
        )


def _notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType,
    priority: NotificationPriority,
    action_url: str | None,
    dedupe_key: str,
    metadata: dict,
    now: datetime,
) -> Notification:
    suffix = dedupe_key.replace(":", "_")
    return Notification(
        id=f"not_{suffix}_{now.strftime('%H%M%S%f')}",
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        action_url=action_url,
        metadata={"dedupe_key": dedupe_key, "agent": "notification-agent", **metadata},
        created_at=now,
    )
