from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.agents.notification_agent import NotificationAgent, NotificationRunResult
from app.db.repository import GrantPilotRepository, get_repository
from app.db.seed_data import DEFAULT_USER_ID
from app.models import Notification, NotificationPriority, NotificationType


class NotificationSort(str, Enum):
    CREATED_DESC = "created_desc"
    CREATED_ASC = "created_asc"
    PRIORITY_DESC = "priority_desc"
    PRIORITY_ASC = "priority_asc"


_PRIORITY_ORDER = {
    NotificationPriority.URGENT: 4,
    NotificationPriority.HIGH: 3,
    NotificationPriority.MEDIUM: 2,
    NotificationPriority.LOW: 1,
}


router = APIRouter(prefix="/notifications", tags=["notifications"])


def _filter_and_sort(
    notifications: list[Notification],
    notification_type: NotificationType | None,
    priority: NotificationPriority | None,
    is_read: bool | None,
    sort: NotificationSort,
) -> list[Notification]:
    filtered = notifications
    if notification_type is not None:
        filtered = [item for item in filtered if item.notification_type == notification_type]
    if priority is not None:
        filtered = [item for item in filtered if item.priority == priority]
    if is_read is not None:
        filtered = [item for item in filtered if item.is_read is is_read]

    if sort == NotificationSort.CREATED_ASC:
        return sorted(filtered, key=lambda item: item.created_at)
    if sort == NotificationSort.PRIORITY_DESC:
        return sorted(
            filtered,
            key=lambda item: (_PRIORITY_ORDER.get(item.priority, 0), item.created_at),
            reverse=True,
        )
    if sort == NotificationSort.PRIORITY_ASC:
        return sorted(
            filtered,
            key=lambda item: (_PRIORITY_ORDER.get(item.priority, 0), item.created_at),
        )
    return sorted(filtered, key=lambda item: item.created_at, reverse=True)


@router.get("", response_model=list[Notification])
def list_notifications(
    notification_type: NotificationType | None = Query(default=None, alias="type"),
    priority: NotificationPriority | None = None,
    is_read: bool | None = None,
    sort: NotificationSort = NotificationSort.CREATED_DESC,
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[Notification]:
    notifications = repository.list_notifications()
    return _filter_and_sort(notifications, notification_type, priority, is_read, sort)


@router.post("/run", response_model=NotificationRunResult)
async def run_notification_agent(
    repository: GrantPilotRepository = Depends(get_repository),
) -> NotificationRunResult:
    agent = NotificationAgent(repository)
    return await agent.generate_notifications(DEFAULT_USER_ID)


@router.post("", response_model=Notification, status_code=201)
def create_notification(
    payload: Notification,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Notification:
    return repository.create_record(payload)


@router.patch("/read-all", response_model=list[Notification])
def mark_all_notifications_read(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[Notification]:
    updated: list[Notification] = []
    for notification in repository.list_notifications():
        if not notification.is_read:
            updated.append(repository.mark_notification_read(notification.id))
    return updated


@router.get("/{notification_id}", response_model=Notification)
def get_notification(
    notification_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Notification:
    try:
        return repository.get_record(Notification, notification_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{notification_id}/read", response_model=Notification)
def mark_notification_read(
    notification_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Notification:
    try:
        return repository.mark_notification_read(notification_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/{notification_id}", response_model=Notification)
def update_notification(
    notification_id: str,
    payload: Notification,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Notification:
    try:
        return repository.update_record(
            Notification,
            notification_id,
            payload.model_dump(mode="json"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(Notification, notification_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
