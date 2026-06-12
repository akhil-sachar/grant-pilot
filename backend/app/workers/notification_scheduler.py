from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from app.agents.notification_agent import NotificationAgent
from app.config import get_settings
from app.db.repository import get_repository
from app.workers.sync_worker import WorkerRunResult

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None


async def run_notification_scan() -> WorkerRunResult:
    repository = get_repository()
    agent = NotificationAgent(repository)
    result = await agent.generate_notifications()
    return WorkerRunResult(
        worker_name="notification-scan",
        status="completed",
        message=f"Created {result.created_count} notifications.",
    )


async def _scheduler_loop(interval_seconds: int) -> None:
    while True:
        try:
            result = await run_notification_scan()
            logger.info("Notification scan completed: %s", result.message)
        except Exception:
            logger.exception("Notification scan failed")
        await asyncio.sleep(interval_seconds)


def start_notification_scheduler() -> None:
    global _scheduler_task
    settings = get_settings()
    if not settings.notification_scan_enabled:
        logger.info("Notification scan scheduler disabled")
        return
    if _scheduler_task is not None and not _scheduler_task.done():
        return

    loop = asyncio.get_event_loop()
    _scheduler_task = loop.create_task(_scheduler_loop(settings.notification_scan_interval_seconds))
    logger.info(
        "Notification scan scheduler started (interval=%ss)",
        settings.notification_scan_interval_seconds,
    )


async def stop_notification_scheduler() -> None:
    global _scheduler_task
    if _scheduler_task is not None:
        _scheduler_task.cancel()
        with suppress(asyncio.CancelledError):
            await _scheduler_task
        _scheduler_task = None
