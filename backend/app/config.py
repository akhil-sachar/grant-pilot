from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "GrantPilot API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    demo_mode: bool = True
    clickhouse_enabled: bool = True
    clickhouse_fallback_enabled: bool = True
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    mock_storage_path: Path = BACKEND_DIR / ".data" / "mock_storage.json"
    document_storage_path: Path = BACKEND_DIR / ".data" / "documents"

    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_database: str = "grantpilot"
    clickhouse_user: str = "default"
    clickhouse_password: str = ""

    sponsor_scan_enabled: bool = True
    sponsor_scan_interval_seconds: int = 300
    notification_scan_enabled: bool = True
    notification_scan_interval_seconds: int = 180
    composio_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    agent_generation_method: str = "auto"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_enabled: bool = True
    guild_home: str = ".guild"
    guild_ai_enabled: bool = True
    openui_url: str = "http://localhost:7878"
    openui_enabled: bool = True
    demo_auto_run: bool = False

    grants_gov_live_enabled: bool = True
    grants_gov_api_url: str = "https://api.grants.gov/v1/api/search2"
    grants_gov_search_rows: int = 25
    grants_gov_search_keyword: str = "education scholarship student"
    grants_gov_opp_statuses: str = "forecasted|posted"
    grants_gov_search_agencies: str = ""
    grants_gov_funding_categories: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("mock_storage_path", mode="after")
    @classmethod
    def resolve_mock_storage_path(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return (PROJECT_ROOT / value).resolve()

    @field_validator("document_storage_path", mode="after")
    @classmethod
    def resolve_document_storage_path(cls, value: Path) -> Path:
        if value.is_absolute():
            return value
        return (PROJECT_ROOT / value).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
