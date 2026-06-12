from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from app.agents.sponsor_agent import SponsorAgent
from app.config import get_settings
from app.db.repository import get_repository
from app.services.scan_state import get_scan_tracker
from app.workers.sync_worker import WorkerRunResult

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None


async def run_sponsor_scan() -> WorkerRunResult:
    repository = get_repository()
    agent = SponsorAgent(repository)
    result = await agent.scan_all()
    return WorkerRunResult(
        worker_name="sponsor-scan",
        status=result.status,
        message=result.summary,
    )


def get_scan_status() -> dict:
    repository = get_repository()
    tracker = get_scan_tracker()
    runs = sorted(
        repository.list_ingestion_runs(),
        key=lambda run: run.started_at,
        reverse=True,
    )[:20]
    status = tracker.snapshot(
        total_opportunities=len(repository.list_opportunities()),
        recent_ingestion_runs=runs,
    )
    return status.model_dump(mode="json")


async def _scheduler_loop(interval_seconds: int) -> None:
    while True:
        try:
            result = await run_sponsor_scan()
            logger.info("Sponsor scan completed: %s", result.message)
        except Exception:
            logger.exception("Sponsor scan failed")
        await asyncio.sleep(interval_seconds)


def start_scan_scheduler() -> None:
    global _scheduler_task
    settings = get_settings()
    if not settings.sponsor_scan_enabled:
        logger.info("Sponsor scan scheduler disabled")
        return
    if _scheduler_task is not None and not _scheduler_task.done():
        return

    loop = asyncio.get_event_loop()
    _scheduler_task = loop.create_task(_scheduler_loop(settings.sponsor_scan_interval_seconds))
    logger.info(
        "Sponsor scan scheduler started (interval=%ss)",
        settings.sponsor_scan_interval_seconds,
    )


async def stop_scan_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task is not None:
        _scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await _scheduler_task
        _scheduler_task = None


def run_once() -> WorkerRunResult:
    """Synchronous entry point for CLI scripts."""
    return asyncio.run(run_sponsor_scan())
