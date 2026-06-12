from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import Settings
from app.db.seed_data import DEFAULT_USER_ID
from app.models import (
    DocumentProcessingStatus,
    DocumentType,
    DocumentVersion,
    UploadedDocument,
)


SUPPORTED_UPLOAD_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/octet-stream",
}


def make_preview(text: str | None, length: int = 220) -> str | None:
    if not text:
        return None
    normalized = " ".join(text.split())
    if len(normalized) <= length:
        return normalized
    return f"{normalized[: length - 3]}..."


def extract_text_from_bytes(content: bytes, mime_type: str, file_name: str) -> str:
    if mime_type == "application/pdf" or file_name.lower().endswith(".pdf"):
        return _extract_pdf_text(content)
    if mime_type.startswith("text/") or file_name.lower().endswith((".txt", ".md")):
        return content.decode("utf-8", errors="replace")
    return ""


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page.strip() for page in pages if page.strip())


def build_uploaded_document(
    *,
    settings: Settings,
    upload: UploadFile,
    content: bytes,
    document_type: DocumentType,
    user_id: str = DEFAULT_USER_ID,
    tags: list[str] | None = None,
) -> tuple[UploadedDocument, DocumentVersion]:
    now = datetime.now(timezone.utc)
    document_id = f"doc_{uuid4().hex[:12]}"
    version_id = f"docver_{uuid4().hex[:12]}"
    file_name = upload.filename or f"{document_id}.bin"
    mime_type = upload.content_type or "application/octet-stream"
    storage_uri = _save_file(
        settings.document_storage_path,
        user_id=user_id,
        document_id=document_id,
        version_id=version_id,
        file_name=file_name,
        content=content,
    )
    extracted_text = extract_text_from_bytes(content, mime_type, file_name)
    preview = make_preview(extracted_text)
    metadata = {
        "original_file_name": file_name,
        "storage_backend": "local_file",
        "text_extraction": "complete" if extracted_text else "empty",
    }

    document = UploadedDocument(
        id=document_id,
        user_id=user_id,
        file_name=file_name,
        document_type=document_type,
        storage_uri=storage_uri,
        mime_type=mime_type,
        size_bytes=len(content),
        extracted_text=extracted_text,
        extracted_text_preview=preview,
        current_version_id=version_id,
        version_number=1,
        tags=tags or [document_type.value],
        metadata=metadata,
        status=DocumentProcessingStatus.PROCESSED,
        uploaded_at=now,
        updated_at=now,
    )
    version = DocumentVersion(
        id=version_id,
        document_id=document_id,
        user_id=user_id,
        version_number=1,
        file_name=file_name,
        storage_uri=storage_uri,
        mime_type=mime_type,
        size_bytes=len(content),
        extracted_text=extracted_text,
        extracted_text_preview=preview,
        metadata=metadata,
        created_at=now,
    )
    return document, version


def build_next_document_version(
    *,
    settings: Settings,
    current_document: UploadedDocument,
    upload: UploadFile,
    content: bytes,
) -> tuple[UploadedDocument, DocumentVersion]:
    now = datetime.now(timezone.utc)
    version_number = current_document.version_number + 1
    version_id = f"docver_{uuid4().hex[:12]}"
    file_name = upload.filename or current_document.file_name
    mime_type = upload.content_type or current_document.mime_type
    storage_uri = _save_file(
        settings.document_storage_path,
        user_id=current_document.user_id,
        document_id=current_document.id,
        version_id=version_id,
        file_name=file_name,
        content=content,
    )
    extracted_text = extract_text_from_bytes(content, mime_type, file_name)
    preview = make_preview(extracted_text)
    metadata = {
        **current_document.metadata,
        "original_file_name": file_name,
        "storage_backend": "local_file",
        "text_extraction": "complete" if extracted_text else "empty",
    }

    updated_document = current_document.model_copy(
        update={
            "file_name": file_name,
            "storage_uri": storage_uri,
            "mime_type": mime_type,
            "size_bytes": len(content),
            "extracted_text": extracted_text,
            "extracted_text_preview": preview,
            "current_version_id": version_id,
            "version_number": version_number,
            "metadata": metadata,
            "status": DocumentProcessingStatus.PROCESSED,
            "updated_at": now,
        }
    )
    version = DocumentVersion(
        id=version_id,
        document_id=current_document.id,
        user_id=current_document.user_id,
        version_number=version_number,
        file_name=file_name,
        storage_uri=storage_uri,
        mime_type=mime_type,
        size_bytes=len(content),
        extracted_text=extracted_text,
        extracted_text_preview=preview,
        metadata=metadata,
        created_at=now,
    )
    return updated_document, version


def _save_file(
    root: Path,
    *,
    user_id: str,
    document_id: str,
    version_id: str,
    file_name: str,
    content: bytes,
) -> str:
    safe_name = Path(file_name).name
    target_dir = root / user_id / document_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{version_id}_{safe_name}"
    target_path.write_bytes(content)
    return str(target_path)

