from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import UserProfile, UserProfileUpdate


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=list[UserProfile])
def list_profiles(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[UserProfile]:
    return repository.list_records(UserProfile)


@router.post("", response_model=UserProfile, status_code=201)
def create_profile(
    payload: UserProfile,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UserProfile:
    return repository.create_record(payload)


@router.get("/me", response_model=UserProfile)
def read_profile(repository: GrantPilotRepository = Depends(get_repository)) -> UserProfile:
    try:
        return repository.get_user_profile()
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put("/me", response_model=UserProfile)
def update_profile(
    payload: UserProfileUpdate,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UserProfile:
    try:
        return repository.update_user_profile(payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/{user_id}", response_model=UserProfile)
def get_profile(
    user_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UserProfile:
    try:
        return repository.get_record(UserProfile, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{user_id}", response_model=UserProfile)
def update_profile_by_id(
    user_id: str,
    payload: UserProfileUpdate,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UserProfile:
    try:
        return repository.update_user_profile(payload, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=204)
def delete_profile(
    user_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(UserProfile, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
