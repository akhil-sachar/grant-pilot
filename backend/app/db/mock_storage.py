from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from threading import RLock
from typing import TypeVar
from uuid import uuid4

import json

from app.config import get_settings
from app.db.seed_data import DEFAULT_USER_ID, build_seed_data
from app.models import (
    AgentActionLog,
    Application,
    EssayVersion,
    MatchResult,
    Notification,
    Opportunity,
    OutreachEmail,
    RecommendationDraft,
    UploadedDocument,
    UploadedDocumentCreate,
    UserProfile,
    UserProfileUpdate,
    IngestionRun,
)
from app.models.uploaded_document import DocumentProcessingStatus


T = TypeVar("T")


class MockStorage:
    def __init__(self, path: Path):
        self.path = path
        self._lock = RLock()
        self._data = self._load_or_seed()

    def _load_or_seed(self) -> dict[str, list[dict]]:
        seed_data = build_seed_data()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            changed = False
            for collection, seed_records in seed_data.items():
                existing = data.setdefault(collection, [])
                existing_ids = {item.get("id") for item in existing}
                for record in seed_records:
                    if record.get("id") not in existing_ids:
                        existing.append(record)
                        changed = True
            if changed:
                self._persist(data)
            return data

        self._persist(seed_data)
        return seed_data

    def _persist(self, data: dict[str, list[dict]] | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data or self._data, handle, indent=2)

    def _list(self, collection: str, model: type[T]) -> list[T]:
        return [model.model_validate(item) for item in self._data.get(collection, [])]

    @property
    def storage_mode(self) -> str:
        return "local"

    def initialize(self) -> None:
        self._load_or_seed()

    def list_collection(self, collection: str, model: type[T]) -> list[T]:
        return self._list(collection, model)

    def get_record(self, collection: str, model: type[T], record_id: str) -> T:
        for record in self._list(collection, model):
            if getattr(record, "id") == record_id:
                return record
        raise KeyError(f"Record not found in {collection}: {record_id}")

    def upsert_record(self, collection: str, record: T) -> T:
        with self._lock:
            records = self._data.setdefault(collection, [])
            dumped = record.model_dump(mode="json")
            for index, item in enumerate(records):
                if item.get("id") == dumped["id"]:
                    records[index] = dumped
                    self._persist()
                    return record
            records.append(dumped)
            self._persist()
            return record

    def update_record(
        self,
        collection: str,
        model: type[T],
        record_id: str,
        payload: dict,
    ) -> T:
        current = self.get_record(collection, model, record_id)
        merged = current.model_dump(mode="json")
        merged.update({key: value for key, value in payload.items() if value is not None})
        if "updated_at" in merged:
            merged["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated = model.model_validate(merged)
        return self.upsert_record(collection, updated)

    def delete_record(self, collection: str, record_id: str) -> None:
        with self._lock:
            records = self._data.setdefault(collection, [])
            remaining = [item for item in records if item.get("id") != record_id]
            if len(remaining) == len(records):
                raise KeyError(f"Record not found in {collection}: {record_id}")
            self._data[collection] = remaining
            self._persist()

    def get_user_profile(self, user_id: str = DEFAULT_USER_ID) -> UserProfile:
        profiles = self._list("user_profiles", UserProfile)
        for profile in profiles:
            if profile.id == user_id:
                return profile
        raise KeyError(f"Profile not found: {user_id}")

    def update_user_profile(
        self,
        payload: UserProfileUpdate,
        user_id: str = DEFAULT_USER_ID,
    ) -> UserProfile:
        with self._lock:
            for index, item in enumerate(self._data["user_profiles"]):
                if item["id"] == user_id:
                    merged = {
                        **item,
                        **payload.model_dump(exclude_unset=True, mode="json"),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self._data["user_profiles"][index] = merged
                    self._persist()
                    return UserProfile.model_validate(merged)
        raise KeyError(f"Profile not found: {user_id}")

    def list_documents(self, user_id: str = DEFAULT_USER_ID) -> list[UploadedDocument]:
        return [
            document
            for document in self._list("uploaded_documents", UploadedDocument)
            if document.user_id == user_id
        ]

    def create_document(
        self,
        payload: UploadedDocumentCreate,
        user_id: str = DEFAULT_USER_ID,
    ) -> UploadedDocument:
        with self._lock:
            document_id = f"doc_{uuid4().hex[:10]}"
            document = UploadedDocument(
                id=document_id,
                user_id=user_id,
                file_name=payload.file_name,
                document_type=payload.document_type,
                storage_uri=f"mock://documents/{document_id}/{payload.file_name}",
                mime_type=payload.mime_type,
                size_bytes=payload.size_bytes,
                tags=payload.tags,
                metadata=payload.metadata,
                status=DocumentProcessingStatus.UPLOADED,
                uploaded_at=datetime.now(timezone.utc),
            )
            self._data["uploaded_documents"].append(document.model_dump(mode="json"))
            self._persist()
            return document

    def list_opportunities(self) -> list[Opportunity]:
        return self._list("opportunities", Opportunity)

    def get_opportunity(self, opportunity_id: str) -> Opportunity:
        for opportunity in self.list_opportunities():
            if opportunity.id == opportunity_id:
                return opportunity
        raise KeyError(f"Opportunity not found: {opportunity_id}")

    def list_matches(self, user_id: str = DEFAULT_USER_ID) -> list[MatchResult]:
        return [
            match
            for match in self._list("match_results", MatchResult)
            if match.user_id == user_id
        ]

    def list_applications(self, user_id: str = DEFAULT_USER_ID) -> list[Application]:
        return [
            application
            for application in self._list("applications", Application)
            if application.user_id == user_id
        ]

    def get_application(self, application_id: str) -> Application:
        for application in self._list("applications", Application):
            if application.id == application_id:
                return application
        raise KeyError(f"Application not found: {application_id}")

    def list_essay_versions(self, application_id: str | None = None) -> list[EssayVersion]:
        essays = self._list("essay_versions", EssayVersion)
        if application_id is None:
            return essays
        return [essay for essay in essays if essay.application_id == application_id]

    def list_recommendation_drafts(
        self,
        application_id: str | None = None,
    ) -> list[RecommendationDraft]:
        drafts = self._list("recommendation_drafts", RecommendationDraft)
        if application_id is None:
            return drafts
        return [draft for draft in drafts if draft.application_id == application_id]

    def list_outreach_emails(self, application_id: str | None = None) -> list[OutreachEmail]:
        emails = self._list("outreach_emails", OutreachEmail)
        if application_id is None:
            return emails
        return [email for email in emails if email.application_id == application_id]

    def list_notifications(self, user_id: str = DEFAULT_USER_ID) -> list[Notification]:
        return [
            notification
            for notification in self._list("notifications", Notification)
            if notification.user_id == user_id
        ]

    def mark_notification_read(self, notification_id: str) -> Notification:
        with self._lock:
            for index, item in enumerate(self._data["notifications"]):
                if item["id"] == notification_id:
                    item = {**item, "is_read": True}
                    self._data["notifications"][index] = item
                    self._persist()
                    return Notification.model_validate(item)
        raise KeyError(f"Notification not found: {notification_id}")

    def list_agent_action_logs(self, user_id: str = DEFAULT_USER_ID) -> list[AgentActionLog]:
        return [
            log
            for log in self._list("agent_action_logs", AgentActionLog)
            if log.user_id == user_id
        ]

    def list_ingestion_runs(self) -> list[IngestionRun]:
        return sorted(
            self._list("ingestion_runs", IngestionRun),
            key=lambda run: run.started_at,
            reverse=True,
        )


@lru_cache
def get_storage() -> MockStorage:
    settings = get_settings()
    return MockStorage(settings.mock_storage_path)
