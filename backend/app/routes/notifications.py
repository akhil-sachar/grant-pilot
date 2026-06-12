from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import Notification


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[Notification])
def list_notifications(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[Notification]:
    return repository.list_notifications()


@router.post("", response_model=Notification, status_code=201)
def create_notification(
    payload: Notification,
    repository: GrantPilotRepository = Depends(get_repository),
) -> Notification:
    return repository.create_record(payload)


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
