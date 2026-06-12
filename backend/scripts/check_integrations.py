"""Check integration connectivity. Run: python scripts/check_integrations.py"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def status(name: str, ok: bool, detail: str = "") -> None:
    mark = "OK" if ok else "FAIL"
    line = f"[{mark}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)


def check_clickhouse() -> None:
    from app.config import get_settings

    settings = get_settings()
    if not settings.clickhouse_enabled:
        status("ClickHouse", True, "disabled (CLICKHOUSE_ENABLED=false)")
        return
    try:
        import clickhouse_connect

        client = clickhouse_connect.get_client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            username=settings.clickhouse_user,
            password=settings.clickhouse_password,
            database="default",
        )
        client.command("SELECT 1")
        db = settings.clickhouse_database
        if " " in db:
            status("ClickHouse", False, f"database name invalid: '{db}' (use grantpilot, no spaces)")
            return
        client_db = clickhouse_connect.get_client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            username=settings.clickhouse_user,
            password=settings.clickhouse_password,
            database=db,
        )
        client_db.command("SELECT 1")
        status("ClickHouse", True, f"connected to {settings.clickhouse_host}:{settings.clickhouse_port}/{db}")
    except Exception as exc:
        status("ClickHouse", False, str(exc)[:120])


def check_openai() -> None:
    from app.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        status("OpenAI", False, "OPENAI_API_KEY not set")
        return
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        models = client.models.list()
        _ = next(iter(models.data), None)
        status("OpenAI", True, f"authenticated (model config: {settings.openai_model})")
    except Exception as exc:
        status("OpenAI", False, str(exc)[:120])


def check_langfuse() -> None:
    from app.config import get_settings

    settings = get_settings()
    if not settings.langfuse_enabled:
        status("Langfuse", True, "disabled")
        return
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        status("Langfuse", False, "LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY missing")
        return
    try:
        import httpx

        response = httpx.get(
            f"{settings.langfuse_host.rstrip('/')}/api/public/health",
            auth=(settings.langfuse_public_key, settings.langfuse_secret_key),
            timeout=15.0,
        )
        if response.status_code == 200:
            status("Langfuse", True, f"reachable at {settings.langfuse_host}")
        else:
            status("Langfuse", False, f"HTTP {response.status_code}")
    except Exception as exc:
        status("Langfuse", False, str(exc)[:120])


def check_composio() -> None:
    from app.config import get_settings
    from app.services.composio_service import get_composio_service

    settings = get_settings()
    if not settings.composio_api_key:
        status("Composio", False, "COMPOSIO_API_KEY not set (simulated mode only)")
        return
    if settings.demo_mode:
        status("Composio", True, "key set but DEMO_MODE=true keeps simulated mode")
        return
    svc = get_composio_service()
    status("Composio", svc.mode.value == "live", f"mode={svc.mode.value}")


async def check_grants_gov() -> None:
    from app.adapters.funding.grants_gov_client import GrantsGovClient

    client = GrantsGovClient()
    if not client.enabled:
        status("Grants.gov API", True, "disabled (GRANTS_GOV_LIVE_ENABLED=false)")
        return
    try:
        records = await client.search_opportunities()
        status("Grants.gov API", True, f"{len(records)} opportunities returned")
    except Exception as exc:
        status("Grants.gov API", False, str(exc)[:120])


def check_repository() -> None:
    try:
        from app.db.repository import get_repository

        repo = get_repository()
        repo.initialize()
        health = repo.health()
        status(
            "App storage",
            True,
            f"mode={health.get('storage_mode')} primary_available={health.get('primary_available')}",
        )
    except Exception as exc:
        status("App storage", False, str(exc)[:120])


def main() -> None:
    from app.config import get_settings

    s = get_settings()
    print("GrantPilot integration check\n")
    print(f"  DEMO_MODE={s.demo_mode}  AGENT_GENERATION_METHOD={s.agent_generation_method}\n")
    check_clickhouse()
    check_openai()
    check_langfuse()
    check_composio()
    asyncio.run(check_grants_gov())
    check_repository()
    print()


if __name__ == "__main__":
    main()
