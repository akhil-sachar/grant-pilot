from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import get_settings
from app.db.clickhouse_service import ClickHouseService, ClickHouseStorageError, TABLES
from app.db.mock_storage import MockStorage
from app.db.seed_data import DEFAULT_USER_ID, build_seed_data
from app.models import (
    AgentActionLog,
    Application,
    EssayVersion,
    IngestionRun,
    IngestionRunStatus,
    MatchResult,
    Notification,
    Opportunity,
    OutreachEmail,
    RecommendationDraft,
    UploadedDocument,
    UploadedDocumentCreate,
    UserProfile,
    UserProfileUpdate,
)
from app.models.uploaded_document import DocumentProcessingStatus


T = TypeVar("T", bound=BaseModel)


MODEL_COLLECTIONS: dict[type[BaseModel], str] = {
    config.model: config.collection_name for config in TABLES.values()
}


class GrantPilotRepository:
    def __init__(
        self,
        primary: ClickHouseService | None,
        fallback: MockStorage,
        fallback_enabled: bool = True,
    ):
        self.primary = primary
        self.fallback = fallback
        self.fallback_enabled = fallback_enabled
        self.last_error: str | None = None
        self._using_fallback = primary is None

    @property
    def storage_mode(self) -> str:
        if self.primary is not None and not self._using_fallback:
            return self.primary.storage_mode
        return self.fallback.storage_mode

    def initialize(self) -> None:
        if self.primary is None:
            self.fallback.initialize()
            return
        try:
            self.primary.initialize()
            self._using_fallback = False
        except ClickHouseStorageError as exc:
            self._handle_primary_error(exc)

    def health(self) -> dict[str, Any]:
        primary_available = False
        if self.primary is not None and not self._using_fallback:
            primary_available = self.primary.ping()
            if primary_available:
                self._using_fallback = False
        return {
            "storage_mode": self.storage_mode,
            "primary": "clickhouse" if self.primary is not None else None,
            "primary_available": primary_available,
            "fallback_enabled": self.fallback_enabled,
            "last_error": self.last_error,
        }

    def list_records(self, model: type[T], where: str | None = None) -> list[T]:
        collection = self._collection_for_model(model)
        if self._should_try_primary():
            try:
                records = self.primary.list_records(collection, model, where=where)
                self._using_fallback = False
                return records
            except ClickHouseStorageError as exc:
                self._handle_primary_error(exc)
        return self.fallback.list_collection(collection, model)

    def get_record(self, model: type[T], record_id: str) -> T:
        collection = self._collection_for_model(model)
        if self._should_try_primary():
            try:
                record = self.primary.get_record(collection, model, record_id)
                self._using_fallback = False
                return record
            except ClickHouseStorageError as exc:
                self._handle_primary_error(exc)
        return self.fallback.get_record(collection, model, record_id)

    def create_record(self, record: T) -> T:
        collection = self._collection_for_model(type(record))
        if self._should_try_primary():
            try:
                self.primary.upsert_model(record)
                self._using_fallback = False
                return record
            except ClickHouseStorageError as exc:
                self._handle_primary_error(exc)
        return self.fallback.upsert_record(collection, record)

    def update_record(self, model: type[T], record_id: str, payload: dict[str, Any]) -> T:
        collection = self._collection_for_model(model)
        if self._should_try_primary():
            try:
                updated = self.primary.update_record(collection, record_id, payload, model)
                self._using_fallback = False
                return updated
            except ClickHouseStorageError as exc:
                self._handle_primary_error(exc)
        return self.fallback.update_record(collection, model, record_id, payload)

    def delete_record(self, model: type[BaseModel], record_id: str) -> None:
        collection = self._collection_for_model(model)
        if self._should_try_primary():
            try:
                self.primary.delete_record(collection, record_id)
                self._using_fallback = False
                return
            except ClickHouseStorageError as exc:
                self._handle_primary_error(exc)
        self.fallback.delete_record(collection, record_id)

    def load_sample_data(self) -> IngestionRun:
        seed_data = build_seed_data()
        seen = sum(len(records) for records in seed_data.values())
        loaded = 0
        for collection, records in seed_data.items():
            model = TABLES[collection].model
            for record in records:
                self.create_record(model.model_validate(record))
                loaded += 1

        ingestion_run = IngestionRun(
            id=f"ingest_sample_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            source_name="sample_data_loader",
            status=IngestionRunStatus.COMPLETED,
            records_seen=seen,
            records_loaded=loaded,
            metadata={"storage_mode": self.storage_mode},
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        self.create_record(ingestion_run)
        return ingestion_run

    def get_user_profile(self, user_id: str = DEFAULT_USER_ID) -> UserProfile:
        return self.get_record(UserProfile, user_id)

    def update_user_profile(
        self,
        payload: UserProfileUpdate,
        user_id: str = DEFAULT_USER_ID,
    ) -> UserProfile:
        return self.update_record(
            UserProfile,
            user_id,
            payload.model_dump(exclude_unset=True, mode="json"),
        )

    def list_documents(self, user_id: str = DEFAULT_USER_ID) -> list[UploadedDocument]:
        return [document for document in self.list_records(UploadedDocument) if document.user_id == user_id]

    def create_document(
        self,
        payload: UploadedDocumentCreate,
        user_id: str = DEFAULT_USER_ID,
    ) -> UploadedDocument:
        document_id = f"doc_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        document = UploadedDocument(
            id=document_id,
            user_id=user_id,
            file_name=payload.file_name,
            document_type=payload.document_type,
            storage_uri=f"{self.storage_mode}://documents/{document_id}/{payload.file_name}",
            mime_type=payload.mime_type,
            size_bytes=payload.size_bytes,
            tags=payload.tags,
            metadata=payload.metadata,
            status=DocumentProcessingStatus.UPLOADED,
            uploaded_at=datetime.now(timezone.utc),
        )
        return self.create_record(document)

    def list_opportunities(self) -> list[Opportunity]:
        return self.list_records(Opportunity)

    def get_opportunity(self, opportunity_id: str) -> Opportunity:
        return self.get_record(Opportunity, opportunity_id)

    def list_matches(self, user_id: str = DEFAULT_USER_ID) -> list[MatchResult]:
        return [match for match in self.list_records(MatchResult) if match.user_id == user_id]

    def list_applications(self, user_id: str = DEFAULT_USER_ID) -> list[Application]:
        return [
            application
            for application in self.list_records(Application)
            if application.user_id == user_id
        ]

    def get_application(self, application_id: str) -> Application:
        return self.get_record(Application, application_id)

    def list_essay_versions(self, application_id: str | None = None) -> list[EssayVersion]:
        essays = self.list_records(EssayVersion)
        if application_id is None:
            return essays
        return [essay for essay in essays if essay.application_id == application_id]

    def list_recommendation_drafts(
        self,
        application_id: str | None = None,
    ) -> list[RecommendationDraft]:
        drafts = self.list_records(RecommendationDraft)
        if application_id is None:
            return drafts
        return [draft for draft in drafts if draft.application_id == application_id]

    def list_outreach_emails(self, application_id: str | None = None) -> list[OutreachEmail]:
        emails = self.list_records(OutreachEmail)
        if application_id is None:
            return emails
        return [email for email in emails if email.application_id == application_id]

    def list_notifications(self, user_id: str = DEFAULT_USER_ID) -> list[Notification]:
        return [
            notification
            for notification in self.list_records(Notification)
            if notification.user_id == user_id
        ]

    def mark_notification_read(self, notification_id: str) -> Notification:
        return self.update_record(Notification, notification_id, {"is_read": True})

    def list_agent_action_logs(self, user_id: str = DEFAULT_USER_ID) -> list[AgentActionLog]:
        return [log for log in self.list_records(AgentActionLog) if log.user_id == user_id]

    def list_ingestion_runs(self) -> list[IngestionRun]:
        return self.list_records(IngestionRun)

    def _handle_primary_error(self, exc: ClickHouseStorageError) -> None:
        self.last_error = str(exc)
        self._using_fallback = True
        if not self.fallback_enabled:
            raise exc

    def _should_try_primary(self) -> bool:
        return self.primary is not None and not self._using_fallback

    @staticmethod
    def _collection_for_model(model: type[BaseModel]) -> str:
        collection = MODEL_COLLECTIONS.get(model)
        if collection is None:
            raise KeyError(f"Unsupported model: {model.__name__}")
        return collection


@lru_cache
def get_repository() -> GrantPilotRepository:
    settings = get_settings()
    primary = ClickHouseService(settings) if settings.clickhouse_enabled else None
    fallback = MockStorage(settings.mock_storage_path)
    return GrantPilotRepository(
        primary=primary,
        fallback=fallback,
        fallback_enabled=settings.clickhouse_fallback_enabled,
    )
