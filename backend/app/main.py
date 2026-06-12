from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.clickhouse_service import ClickHouseStorageError
from app.db.repository import get_repository
from app.routes import (
    agent_actions,
    applications,
    config,
    dashboard,
    documents,
    essay_versions,
    health,
    ingestion_runs,
    matches,
    notifications,
    opportunities,
    outreach_emails,
    profile,
    recommendation_drafts,
    storage,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="GrantPilot API foundation with mock storage and stable contracts.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(config.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(profile.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(opportunities.router, prefix=settings.api_prefix)
app.include_router(matches.router, prefix=settings.api_prefix)
app.include_router(applications.router, prefix=settings.api_prefix)
app.include_router(essay_versions.router, prefix=settings.api_prefix)
app.include_router(recommendation_drafts.router, prefix=settings.api_prefix)
app.include_router(outreach_emails.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
app.include_router(agent_actions.router, prefix=settings.api_prefix)
app.include_router(ingestion_runs.router, prefix=settings.api_prefix)
app.include_router(storage.router, prefix=settings.api_prefix)


@app.on_event("startup")
def startup_storage() -> None:
    get_repository().initialize()


@app.exception_handler(ClickHouseStorageError)
def clickhouse_exception_handler(
    _request: Request,
    exc: ClickHouseStorageError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "storage": "clickhouse"},
    )


@app.exception_handler(KeyError)
def key_error_handler(_request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }
