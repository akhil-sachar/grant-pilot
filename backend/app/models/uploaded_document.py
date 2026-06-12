from datetime import datetime
from enum import Enum

from pydantic import Field

from app.models.base import APIModel, Metadata


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
    extracted_text_preview: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)
    status: DocumentProcessingStatus = DocumentProcessingStatus.UPLOADED
    uploaded_at: datetime


class UploadedDocumentCreate(APIModel):
    file_name: str
    document_type: DocumentType
    mime_type: str = "application/octet-stream"
    size_bytes: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=dict)

