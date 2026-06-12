from fastapi import APIRouter, Depends

from fastapi import HTTPException, status

from app.db.repository import GrantPilotRepository, get_repository
from app.models import UploadedDocument, UploadedDocumentCreate


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[UploadedDocument])
def list_documents(
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[UploadedDocument]:
    return repository.list_documents()


@router.post("", response_model=UploadedDocument, status_code=201)
def create_document(
    payload: UploadedDocumentCreate,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UploadedDocument:
    return repository.create_document(payload)


@router.get("/{document_id}", response_model=UploadedDocument)
def get_document(
    document_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UploadedDocument:
    try:
        return repository.get_record(UploadedDocument, document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{document_id}", response_model=UploadedDocument)
def update_document(
    document_id: str,
    payload: UploadedDocument,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UploadedDocument:
    try:
        return repository.update_record(
            UploadedDocument,
            document_id,
            payload.model_dump(mode="json"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> None:
    try:
        repository.delete_record(UploadedDocument, document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
