from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.db.repository import GrantPilotRepository
from app.models import APIModel, AgentActionLog, AgentActionStatus


class ComposioMode(str, Enum):
    SIMULATED = "simulated"
    LIVE = "live"


class ComposioActionResult(APIModel):
    action: str
    provider: str
    status: str
    mode: ComposioMode
    detail: str
    metadata: dict[str, Any] = {}


class ComposioStatus(APIModel):
    mode: ComposioMode
    api_key_configured: bool
    connected_tools: list[str]
    message: str


class ComposioService:
    """Composio integration for Gmail, Google Docs, Calendar, and Drive."""

    TOOLS = ("gmail", "google_docs", "google_calendar", "google_drive")

    def __init__(
        self,
        settings: Settings | None = None,
        repository: GrantPilotRepository | None = None,
    ):
        self.settings = settings or get_settings()
        self.repository = repository
        self.api_key = self.settings.composio_api_key
        self.base_url = "https://backend.composio.dev/api/v3"

    @property
    def mode(self) -> ComposioMode:
        if self.api_key and not self.settings.demo_mode:
            return ComposioMode.LIVE
        return ComposioMode.SIMULATED

    def status(self) -> ComposioStatus:
        if self.mode == ComposioMode.LIVE:
            return ComposioStatus(
                mode=ComposioMode.LIVE,
                api_key_configured=True,
                connected_tools=list(self.TOOLS),
                message="Composio live mode enabled. Actions execute against connected Google tools.",
            )
        return ComposioStatus(
            mode=ComposioMode.SIMULATED,
            api_key_configured=bool(self.api_key),
            connected_tools=list(self.TOOLS),
            message="Composio simulated mode active. Actions are logged without external side effects.",
        )

    async def draft_email(
        self,
        user_id: str,
        to: str,
        subject: str,
        body: str,
    ) -> ComposioActionResult:
        return await self._execute(
            user_id=user_id,
            action="draft_email",
            provider="gmail",
            payload={"to": to, "subject": subject, "body": body},
            simulated_detail=f"Simulated Gmail draft to {to}: {subject}",
        )

    async def create_google_doc(
        self,
        user_id: str,
        title: str,
        content: str,
    ) -> ComposioActionResult:
        return await self._execute(
            user_id=user_id,
            action="create_google_doc",
            provider="google_docs",
            payload={"title": title, "content": content},
            simulated_detail=f"Simulated Google Doc created: {title}",
        )

    async def create_calendar_reminder(
        self,
        user_id: str,
        title: str,
        description: str,
        days_from_now: int = 7,
    ) -> ComposioActionResult:
        when = datetime.now(timezone.utc) + timedelta(days=days_from_now)
        return await self._execute(
            user_id=user_id,
            action="create_calendar_reminder",
            provider="google_calendar",
            payload={"title": title, "description": description, "start_time": when.isoformat()},
            simulated_detail=f"Simulated calendar reminder on {when.date().isoformat()}: {title}",
        )

    async def save_document(
        self,
        user_id: str,
        file_name: str,
        content: str,
    ) -> ComposioActionResult:
        return await self._execute(
            user_id=user_id,
            action="save_document",
            provider="google_drive",
            payload={"file_name": file_name, "content": content},
            simulated_detail=f"Simulated Drive upload: {file_name}",
        )

    async def run_outreach_workflow(
        self,
        user_id: str,
        to: str,
        subject: str,
        body: str,
        follow_up: str,
        doc_title: str,
    ) -> list[ComposioActionResult]:
        return [
            await self.draft_email(user_id, to, subject, body),
            await self.create_google_doc(user_id, doc_title, body),
            await self.create_calendar_reminder(
                user_id,
                title=f"Follow up: {subject}",
                description=follow_up,
            ),
            await self.save_document(user_id, f"{doc_title}.txt", body),
        ]

    async def _execute(
        self,
        user_id: str,
        action: str,
        provider: str,
        payload: dict[str, Any],
        simulated_detail: str,
    ) -> ComposioActionResult:
        if self.mode == ComposioMode.LIVE:
            try:
                result = await self._call_composio(action, payload)
                action_result = ComposioActionResult(
                    action=action,
                    provider=provider,
                    status="completed",
                    mode=ComposioMode.LIVE,
                    detail=result.get("message", f"{action} completed via Composio"),
                    metadata=result,
                )
            except Exception as exc:
                action_result = ComposioActionResult(
                    action=action,
                    provider=provider,
                    status="failed",
                    mode=ComposioMode.LIVE,
                    detail=str(exc),
                    metadata={"payload": payload},
                )
        else:
            action_result = ComposioActionResult(
                action=action,
                provider=provider,
                status="simulated",
                mode=ComposioMode.SIMULATED,
                detail=simulated_detail,
                metadata={"payload": payload},
            )

        self._log_action(user_id, action_result)
        return action_result

    async def _call_composio(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{self.base_url}/actions/{action}/execute",
                headers={"x-api-key": self.api_key},
                json={"input": payload},
            )
            response.raise_for_status()
            return response.json()

    def _log_action(self, user_id: str, result: ComposioActionResult) -> None:
        if self.repository is None:
            return
        log = AgentActionLog(
            id=f"composio_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            user_id=user_id,
            agent_name="composio-service",
            action_type=result.action,
            status=AgentActionStatus.COMPLETED if result.status != "failed" else AgentActionStatus.FAILED,
            input_summary=f"{result.provider} · {result.mode.value} mode",
            output_summary=result.detail,
            metadata={
                "provider": result.provider,
                "mode": result.mode.value,
                "status": result.status,
                **result.metadata,
            },
        )
        self.repository.create_record(log)


def get_composio_service(repository: GrantPilotRepository | None = None) -> ComposioService:
    return ComposioService(repository=repository)
