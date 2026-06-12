from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, TypeVar

import json

import clickhouse_connect
from pydantic import BaseModel

from app.config import Settings
from app.models import (
    AgentActionLog,
    Application,
    DocumentVersion,
    EssayVersion,
    IngestionRun,
    MatchResult,
    Notification,
    Opportunity,
    OutreachEmail,
    RecommendationDraft,
    UploadedDocument,
    UserProfile,
)


T = TypeVar("T", bound=BaseModel)


class ClickHouseStorageError(RuntimeError):
    """Raised when ClickHouse cannot serve a storage request."""


@dataclass(frozen=True)
class TableConfig:
    table_name: str
    collection_name: str
    model: type[BaseModel]
    columns: tuple[str, ...]
    order_by: str
    ddl: str


def _json_dump(value: Any) -> str:
    return json.dumps(value or {}, separators=(",", ":"), default=str)


def _json_load(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def _nullable_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _nullable_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    return date.fromisoformat(str(value)[:10])


TABLES: dict[str, TableConfig] = {
    "user_profiles": TableConfig(
        table_name="user_profiles",
        collection_name="user_profiles",
        model=UserProfile,
        columns=(
            "id",
            "email",
            "full_name",
            "phone",
            "location",
            "date_of_birth",
            "education_level",
            "school_name",
            "major",
            "gpa",
            "graduation_year",
            "fields_of_study",
            "career_goals",
            "research_interests",
            "awards",
            "projects",
            "leadership_experience",
            "citizenship_status",
            "funding_goals",
            "demographic_info_json",
            "preferences_json",
            "created_at",
            "updated_at",
        ),
        order_by="id",
        ddl="""
        CREATE TABLE IF NOT EXISTS user_profiles
        (
            id String,
            email String,
            full_name String,
            phone Nullable(String),
            location Nullable(String),
            date_of_birth Nullable(Date),
            education_level Nullable(String),
            school_name Nullable(String),
            major Nullable(String),
            gpa Nullable(Float32),
            graduation_year Nullable(UInt16),
            fields_of_study Array(String),
            career_goals Array(String),
            research_interests Array(String),
            awards Array(String),
            projects Array(String),
            leadership_experience Array(String),
            citizenship_status Nullable(String),
            funding_goals Array(String),
            demographic_info_json String,
            preferences_json String,
            created_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
    ),
    "uploaded_documents": TableConfig(
        table_name="uploaded_documents",
        collection_name="uploaded_documents",
        model=UploadedDocument,
        columns=(
            "id",
            "user_id",
            "file_name",
            "document_type",
            "storage_uri",
            "mime_type",
            "size_bytes",
            "extracted_text",
            "extracted_text_preview",
            "current_version_id",
            "version_number",
            "tags",
            "metadata_json",
            "status",
            "uploaded_at",
            "updated_at",
        ),
        order_by="uploaded_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS uploaded_documents
        (
            id String,
            user_id String,
            file_name String,
            document_type LowCardinality(String),
            storage_uri String,
            mime_type String,
            size_bytes UInt64,
            extracted_text Nullable(String),
            extracted_text_preview Nullable(String),
            current_version_id Nullable(String),
            version_number UInt16,
            tags Array(String),
            metadata_json String,
            status LowCardinality(String),
            uploaded_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY (user_id, id)
        """,
    ),
    "document_versions": TableConfig(
        table_name="document_versions",
        collection_name="document_versions",
        model=DocumentVersion,
        columns=(
            "id",
            "document_id",
            "user_id",
            "version_number",
            "file_name",
            "storage_uri",
            "mime_type",
            "size_bytes",
            "extracted_text",
            "extracted_text_preview",
            "metadata_json",
            "created_at",
        ),
        order_by="document_id, version_number DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS document_versions
        (
            id String,
            document_id String,
            user_id String,
            version_number UInt16,
            file_name String,
            storage_uri String,
            mime_type String,
            size_bytes UInt64,
            extracted_text Nullable(String),
            extracted_text_preview Nullable(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(created_at)
        ORDER BY (document_id, version_number, id)
        """,
    ),
    "opportunities": TableConfig(
        table_name="opportunities",
        collection_name="opportunities",
        model=Opportunity,
        columns=(
            "id",
            "provider_name",
            "title",
            "description",
            "opportunity_type",
            "amount_min",
            "amount_max",
            "currency",
            "deadline",
            "eligibility_summary",
            "requirements",
            "source_url",
            "status",
            "tags",
            "metadata_json",
            "created_at",
            "updated_at",
        ),
        order_by="deadline ASC NULLS LAST, created_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS opportunities
        (
            id String,
            provider_name String,
            title String,
            description String,
            opportunity_type LowCardinality(String),
            amount_min Nullable(UInt32),
            amount_max Nullable(UInt32),
            currency LowCardinality(String),
            deadline Nullable(Date),
            eligibility_summary String,
            requirements Array(String),
            source_url Nullable(String),
            status LowCardinality(String),
            tags Array(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY id
        """,
    ),
    "match_results": TableConfig(
        table_name="match_results",
        collection_name="match_results",
        model=MatchResult,
        columns=(
            "id",
            "user_id",
            "opportunity_id",
            "score",
            "rationale",
            "strengths",
            "gaps",
            "recommended_actions",
            "status",
            "metadata_json",
            "created_at",
        ),
        order_by="score DESC, created_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS match_results
        (
            id String,
            user_id String,
            opportunity_id String,
            score Float32,
            rationale String,
            strengths Array(String),
            gaps Array(String),
            recommended_actions Array(String),
            status LowCardinality(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(created_at)
        ORDER BY (user_id, opportunity_id, id)
        """,
    ),
    "applications": TableConfig(
        table_name="applications",
        collection_name="applications",
        model=Application,
        columns=(
            "id",
            "user_id",
            "opportunity_id",
            "match_result_id",
            "status",
            "due_at",
            "submitted_at",
            "checklist_json",
            "notes",
            "metadata_json",
            "created_at",
            "updated_at",
        ),
        order_by="due_at ASC NULLS LAST, updated_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS applications
        (
            id String,
            user_id String,
            opportunity_id String,
            match_result_id Nullable(String),
            status LowCardinality(String),
            due_at Nullable(DateTime64(3, 'UTC')),
            submitted_at Nullable(DateTime64(3, 'UTC')),
            checklist_json String,
            notes Nullable(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY (user_id, opportunity_id, id)
        """,
    ),
    "essay_versions": TableConfig(
        table_name="essay_versions",
        collection_name="essay_versions",
        model=EssayVersion,
        columns=(
            "id",
            "application_id",
            "prompt",
            "content",
            "version_number",
            "status",
            "feedback_notes",
            "metadata_json",
            "created_at",
        ),
        order_by="application_id, version_number DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS essay_versions
        (
            id String,
            application_id String,
            prompt String,
            content String,
            version_number UInt16,
            status LowCardinality(String),
            feedback_notes Array(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(created_at)
        ORDER BY (application_id, version_number, id)
        """,
    ),
    "recommendation_drafts": TableConfig(
        table_name="recommendation_drafts",
        collection_name="recommendation_drafts",
        model=RecommendationDraft,
        columns=(
            "id",
            "application_id",
            "recommender_name",
            "recommender_email",
            "relationship",
            "draft_body",
            "status",
            "metadata_json",
            "created_at",
            "updated_at",
        ),
        order_by="updated_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS recommendation_drafts
        (
            id String,
            application_id String,
            recommender_name String,
            recommender_email String,
            relationship String,
            draft_body String,
            status LowCardinality(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY (application_id, id)
        """,
    ),
    "outreach_emails": TableConfig(
        table_name="outreach_emails",
        collection_name="outreach_emails",
        model=OutreachEmail,
        columns=(
            "id",
            "application_id",
            "recipient_email",
            "subject",
            "body",
            "status",
            "sent_at",
            "metadata_json",
            "created_at",
            "updated_at",
        ),
        order_by="updated_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS outreach_emails
        (
            id String,
            application_id String,
            recipient_email String,
            subject String,
            body String,
            status LowCardinality(String),
            sent_at Nullable(DateTime64(3, 'UTC')),
            metadata_json String,
            created_at DateTime64(3, 'UTC'),
            updated_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(updated_at)
        ORDER BY (application_id, id)
        """,
    ),
    "notifications": TableConfig(
        table_name="notifications",
        collection_name="notifications",
        model=Notification,
        columns=(
            "id",
            "user_id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "action_url",
            "metadata_json",
            "created_at",
        ),
        order_by="created_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS notifications
        (
            id String,
            user_id String,
            title String,
            message String,
            notification_type LowCardinality(String),
            is_read Bool,
            action_url Nullable(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC')
        )
        ENGINE = ReplacingMergeTree(created_at)
        ORDER BY (user_id, created_at, id)
        """,
    ),
    "agent_action_logs": TableConfig(
        table_name="agent_action_logs",
        collection_name="agent_action_logs",
        model=AgentActionLog,
        columns=(
            "id",
            "user_id",
            "agent_name",
            "action_type",
            "status",
            "input_summary",
            "output_summary",
            "metadata_json",
            "created_at",
        ),
        order_by="created_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS agent_action_logs
        (
            id String,
            user_id String,
            agent_name LowCardinality(String),
            action_type LowCardinality(String),
            status LowCardinality(String),
            input_summary Nullable(String),
            output_summary Nullable(String),
            metadata_json String,
            created_at DateTime64(3, 'UTC')
        )
        ENGINE = MergeTree
        ORDER BY (user_id, created_at, id)
        """,
    ),
    "ingestion_runs": TableConfig(
        table_name="ingestion_runs",
        collection_name="ingestion_runs",
        model=IngestionRun,
        columns=(
            "id",
            "source_name",
            "status",
            "records_seen",
            "records_loaded",
            "error_message",
            "metadata_json",
            "started_at",
            "completed_at",
        ),
        order_by="started_at DESC",
        ddl="""
        CREATE TABLE IF NOT EXISTS ingestion_runs
        (
            id String,
            source_name LowCardinality(String),
            status LowCardinality(String),
            records_seen UInt64,
            records_loaded UInt64,
            error_message Nullable(String),
            metadata_json String,
            started_at DateTime64(3, 'UTC'),
            completed_at Nullable(DateTime64(3, 'UTC'))
        )
        ENGINE = ReplacingMergeTree(started_at)
        ORDER BY (source_name, started_at, id)
        """,
    ),
}


MODEL_TABLES: dict[type[BaseModel], str] = {
    config.model: table_name for table_name, config in TABLES.items()
}


COMPATIBILITY_ALTERS = (
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS major Nullable(String)",
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS gpa Nullable(Float32)",
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS research_interests Array(String)",
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS awards Array(String)",
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS projects Array(String)",
    "ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS leadership_experience Array(String)",
    "ALTER TABLE uploaded_documents ADD COLUMN IF NOT EXISTS extracted_text Nullable(String)",
    "ALTER TABLE uploaded_documents ADD COLUMN IF NOT EXISTS current_version_id Nullable(String)",
    "ALTER TABLE uploaded_documents ADD COLUMN IF NOT EXISTS version_number UInt16 DEFAULT 1",
    "ALTER TABLE uploaded_documents ADD COLUMN IF NOT EXISTS updated_at DateTime64(3, 'UTC') DEFAULT uploaded_at",
)


class ClickHouseService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Any | None = None
        self._initialized = False

    @property
    def storage_mode(self) -> str:
        return "clickhouse"

    def connect(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            bootstrap_client = clickhouse_connect.get_client(
                host=self.settings.clickhouse_host,
                port=self.settings.clickhouse_port,
                username=self.settings.clickhouse_user,
                password=self.settings.clickhouse_password,
                connect_timeout=2,
                send_receive_timeout=5,
            )
            bootstrap_client.command(
                f"CREATE DATABASE IF NOT EXISTS {self.settings.clickhouse_database}"
            )
            self._client = clickhouse_connect.get_client(
                host=self.settings.clickhouse_host,
                port=self.settings.clickhouse_port,
                username=self.settings.clickhouse_user,
                password=self.settings.clickhouse_password,
                database=self.settings.clickhouse_database,
                connect_timeout=2,
                send_receive_timeout=5,
            )
        except Exception as exc:  # pragma: no cover - depends on external service
            raise ClickHouseStorageError("ClickHouse is unavailable") from exc
        return self._client

    def initialize(self) -> None:
        if self._initialized:
            return
        client = self.connect()
        try:
            for table in TABLES.values():
                client.command(table.ddl)
            for statement in COMPATIBILITY_ALTERS:
                client.command(statement)
        except Exception as exc:  # pragma: no cover - depends on external service
            raise ClickHouseStorageError("Failed to initialize ClickHouse tables") from exc
        self._initialized = True

    def ping(self) -> bool:
        try:
            self.connect().command("SELECT 1")
            return True
        except ClickHouseStorageError:
            return False
        except Exception:
            return False

    def upsert_model(self, record: BaseModel, table_name: str | None = None) -> BaseModel:
        self.initialize()
        resolved_table = table_name or MODEL_TABLES[type(record)]
        config = TABLES[resolved_table]
        row = self._to_row(record, config)
        try:
            self.connect().insert(
                config.table_name,
                [[row[column] for column in config.columns]],
                column_names=list(config.columns),
            )
        except Exception as exc:  # pragma: no cover - depends on external service
            raise ClickHouseStorageError(f"Failed to upsert {config.table_name}") from exc
        return record

    def list_records(
        self,
        table_name: str,
        model: type[T],
        where: str | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[T]:
        self.initialize()
        config = TABLES[table_name]
        query = f"SELECT {', '.join(config.columns)} FROM {config.table_name}"
        if where:
            query += f" WHERE {where}"
        query += f" ORDER BY {order_by or config.order_by}"
        if limit is not None:
            query += f" LIMIT {int(limit)}"

        try:
            rows = self.connect().query(query).named_results()
        except Exception as exc:  # pragma: no cover - depends on external service
            raise ClickHouseStorageError(f"Failed to list {config.table_name}") from exc
        return [model.model_validate(self._from_row(row, config)) for row in rows]

    def get_record(self, table_name: str, model: type[T], record_id: str) -> T:
        rows = self.list_records(
            table_name,
            model,
            where=f"id = {self._quote(record_id)}",
            limit=1,
        )
        if not rows:
            raise KeyError(f"Record not found in {table_name}: {record_id}")
        return rows[0]

    def delete_record(self, table_name: str, record_id: str) -> None:
        self.initialize()
        if table_name not in TABLES:
            raise KeyError(f"Unknown table: {table_name}")
        try:
            self.connect().command(
                f"ALTER TABLE {table_name} DELETE WHERE id = {self._quote(record_id)}"
            )
        except Exception as exc:  # pragma: no cover - depends on external service
            raise ClickHouseStorageError(f"Failed to delete from {table_name}") from exc

    def update_record(
        self,
        table_name: str,
        record_id: str,
        payload: dict[str, Any],
        model: type[T],
    ) -> T:
        current = self.get_record(table_name, model, record_id)
        merged = current.model_dump(mode="json")
        merged.update({key: value for key, value in payload.items() if value is not None})
        if "updated_at" in merged:
            merged["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated = model.model_validate(merged)
        self.upsert_model(updated, table_name)
        return updated

    def _to_row(self, record: BaseModel, config: TableConfig) -> dict[str, Any]:
        data = record.model_dump(mode="python")
        row = dict(data)

        if config.table_name == "user_profiles":
            row["demographic_info_json"] = _json_dump(data.get("demographic_info"))
            row["preferences_json"] = _json_dump(data.get("preferences"))
        elif config.table_name == "applications":
            row["checklist_json"] = _json_dump(data.get("checklist", []))
            row["metadata_json"] = _json_dump(data.get("metadata"))
        elif config.table_name == "match_results":
            meta = dict(data.get("metadata") or {})
            meta.update(
                {
                    "priority": data.get("priority"),
                    "missing_materials": data.get("missing_materials", []),
                    "fit_explanation": data.get("fit_explanation", ""),
                    "funding_potential": data.get("funding_potential", ""),
                    "success_probability": data.get("success_probability", 0),
                }
            )
            row["metadata_json"] = _json_dump(meta)
        elif config.table_name == "essay_versions":
            meta = dict(data.get("metadata") or {})
            meta.update(
                {
                    "source_version_id": data.get("source_version_id"),
                    "change_summary": data.get("change_summary", ""),
                }
            )
            row["metadata_json"] = _json_dump(meta)
        elif config.table_name == "recommendation_drafts":
            meta = dict(data.get("metadata") or {})
            meta.update(
                {
                    "recommender_type": data.get("recommender_type"),
                    "version_number": data.get("version_number", 1),
                    "source_draft_id": data.get("source_draft_id"),
                    "key_talking_points": data.get("key_talking_points", []),
                    "why_it_matches": data.get("why_it_matches", ""),
                }
            )
            row["metadata_json"] = _json_dump(meta)
        elif config.table_name == "outreach_emails":
            meta = dict(data.get("metadata") or {})
            meta.update(
                {
                    "recipient_role": data.get("recipient_role"),
                    "email_type": data.get("email_type"),
                    "suggested_follow_up": data.get("suggested_follow_up", ""),
                    "version_number": data.get("version_number", 1),
                    "source_email_id": data.get("source_email_id"),
                }
            )
            row["metadata_json"] = _json_dump(meta)
        elif config.table_name == "notifications":
            meta = dict(data.get("metadata") or {})
            meta.update({"priority": data.get("priority", "medium")})
            row["metadata_json"] = _json_dump(meta)
        else:
            row["metadata_json"] = _json_dump(data.get("metadata"))

        if "source_url" in row and row["source_url"] is not None:
            row["source_url"] = str(row["source_url"])

        return {column: row.get(column) for column in config.columns}

    def _from_row(self, row: dict[str, Any], config: TableConfig) -> dict[str, Any]:
        data = dict(row)
        if config.table_name == "user_profiles":
            data["demographic_info"] = _json_load(data.pop("demographic_info_json", None), {})
            data["preferences"] = _json_load(data.pop("preferences_json", None), {})
            data["date_of_birth"] = _nullable_date(data.get("date_of_birth"))
        elif config.table_name == "applications":
            data["checklist"] = _json_load(data.pop("checklist_json", None), [])
            data["metadata"] = _json_load(data.pop("metadata_json", None), {})
            data["due_at"] = _nullable_datetime(data.get("due_at"))
            data["submitted_at"] = _nullable_datetime(data.get("submitted_at"))
        elif config.table_name == "match_results":
            meta = _json_load(data.pop("metadata_json", None), {})
            data["priority"] = meta.pop("priority", "medium")
            data["missing_materials"] = meta.pop("missing_materials", [])
            data["fit_explanation"] = meta.pop("fit_explanation", "")
            data["funding_potential"] = meta.pop("funding_potential", "")
            data["success_probability"] = meta.pop("success_probability", 0)
            data["metadata"] = meta
        elif config.table_name == "essay_versions":
            meta = _json_load(data.pop("metadata_json", None), {})
            source_version_id = meta.pop("source_version_id", None)
            if source_version_id is None:
                source_version_id = data.get("source_version_id")
            data["source_version_id"] = source_version_id
            data["change_summary"] = meta.pop("change_summary", data.get("change_summary", ""))
            data["metadata"] = meta
        elif config.table_name == "recommendation_drafts":
            meta = _json_load(data.pop("metadata_json", None), {})
            data["recommender_type"] = meta.pop("recommender_type", "professor")
            data["version_number"] = meta.pop("version_number", data.get("version_number", 1))
            data["source_draft_id"] = meta.pop("source_draft_id", data.get("source_draft_id"))
            data["key_talking_points"] = meta.pop("key_talking_points", [])
            data["why_it_matches"] = meta.pop("why_it_matches", "")
            data["metadata"] = meta
        elif config.table_name == "outreach_emails":
            meta = _json_load(data.pop("metadata_json", None), {})
            data["recipient_role"] = meta.pop("recipient_role", "professor")
            data["email_type"] = meta.pop("email_type", "recommendation_request")
            data["suggested_follow_up"] = meta.pop("suggested_follow_up", "")
            data["version_number"] = meta.pop("version_number", data.get("version_number", 1))
            data["source_email_id"] = meta.pop("source_email_id", data.get("source_email_id"))
            data["metadata"] = meta
        elif config.table_name == "notifications":
            meta = _json_load(data.pop("metadata_json", None), {})
            data["priority"] = meta.pop("priority", "medium")
            data["metadata"] = meta
        else:
            data["metadata"] = _json_load(data.pop("metadata_json", None), {})

        if config.table_name == "opportunities":
            data["deadline"] = _nullable_date(data.get("deadline"))
        if config.table_name == "outreach_emails":
            data["sent_at"] = _nullable_datetime(data.get("sent_at"))
        if config.table_name == "ingestion_runs":
            data["completed_at"] = _nullable_datetime(data.get("completed_at"))

        return data

    @staticmethod
    def _quote(value: str) -> str:
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
