from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.config import Settings, get_settings
from app.db.repository import GrantPilotRepository, get_repository
from app.models import DocumentType, DocumentVersion, UploadedDocument, UploadedDocumentCreate
from app.services.document_service import (
    SUPPORTED_UPLOAD_TYPES,
    build_next_document_version,
    build_uploaded_document,
)


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


@router.post("/upload", response_model=UploadedDocument, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    tags: str = Form(default=""),
    repository: GrantPilotRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> UploadedDocument:
    mime_type = file.content_type or "application/octet-stream"
    if mime_type not in SUPPORTED_UPLOAD_TYPES and not (file.filename or "").lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and text uploads are supported in the vault.",
        )
    content = await file.read()
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    document, version = build_uploaded_document(
        settings=settings,
        upload=file,
        content=content,
        document_type=document_type,
        tags=tag_list,
    )
    return repository.create_document_with_version(document, version)


@router.get("/{document_id}", response_model=UploadedDocument)
def get_document(
    document_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> UploadedDocument:
    try:
        return repository.get_record(UploadedDocument, document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{document_id}/versions", response_model=list[DocumentVersion])
def list_document_versions(
    document_id: str,
    repository: GrantPilotRepository = Depends(get_repository),
) -> list[DocumentVersion]:
    try:
        repository.get_record(UploadedDocument, document_id)
        return repository.list_document_versions(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{document_id}/versions", response_model=UploadedDocument, status_code=201)
async def upload_document_version(
    document_id: str,
    file: UploadFile = File(...),
    repository: GrantPilotRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> UploadedDocument:
    try:
        current_document = repository.get_record(UploadedDocument, document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    content = await file.read()
    document, version = build_next_document_version(
        settings=settings,
        current_document=current_document,
        upload=file,
        content=content,
    )
    return repository.update_document_with_version(document, version)


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
        repository.delete_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
