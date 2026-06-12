from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata, utc_now


class DocumentType(str, Enum):
    RESUME = "resume"
    TRANSCRIPT = "transcript"
    ESSAY = "essay"
    RECOMMENDATION = "recommendation"
    FINANCIAL_AID = "financial_aid"
    IDENTITY = "identity"
    OTHER = "other"


class DocumentProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSED = "processed"
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class UploadedDocument(APIModel):
    id: str
    user_id: str
    file_name: str
    document_type: DocumentType
    storage_uri: str
    mime_type: str
    size_bytes: int = Field(ge=0)
    extracted_text: str | None = None
    extracted_text_preview: str | None = None
    current_version_id: str | None = None
    version_number: int = Field(default=1, ge=1)
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    status: DocumentProcessingStatus = DocumentProcessingStatus.UPLOADED
    uploaded_at: datetime
    updated_at: datetime = Field(default_factory=utc_now)


class UploadedDocumentCreate(APIModel):
    file_name: str
    document_type: DocumentType
    mime_type: str = "application/octet-stream"
    size_bytes: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)


class DocumentVersion(APIModel):
    id: str
    document_id: str
    user_id: str
    version_number: int = Field(ge=1)
    file_name: str
    storage_uri: str
    mime_type: str
    size_bytes: int = Field(ge=0)
    extracted_text: str | None = None
    extracted_text_preview: str | None = None
    metadata: Metadata = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
