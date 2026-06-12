from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import OutreachEmail


router = APIRouter(prefix="/outreach-emails", tags=["outreach emails"])


@router.get("", response_model=list[OutreachEmail])
def list_outreach_emails(
    application_id: str | None = Query(default=None),
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[OutreachEmail]:
    return repository.list_outreach_emails(application_id)


@router.post("", response_model=OutreachEmail, status_code=201)
def create_outreach_email(
    payload: OutreachEmail,
    repository: GrantPilotRepository = Depends(get_repository),
) -> OutreachEmail:
    return repository.create_record(payload)


@router.get("/{email_id}", response_model=OutreachEmail)
def get_outreach_email(
    email_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> OutreachEmail:
    try:
        return repository.get_record(OutreachEmail, email_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{email_id}", response_model=OutreachEmail)
def update_outreach_email(
    email_id: str,
    payload: OutreachEmail,
    repository: GrantPilotRepository = Depends(get_repository),
) -> OutreachEmail:
    try:
        return repository.update_record(OutreachEmail, email_id, payload.model_dump(mode="json"))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{email_id}", status_code=204)
def delete_outreach_email(
    email_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(OutreachEmail, email_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

