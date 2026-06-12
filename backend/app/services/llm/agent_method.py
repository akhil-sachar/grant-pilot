from app.config import get_settings


def resolve_generation_method(explicit: str | None = None) -> str:
    """Return 'openai' when configured, otherwise 'deterministic'."""
    settings = get_settings()
    if explicit and explicit not in {"", "auto"}:
        if explicit in {"ai", "openai"}:
            return "openai" if settings.openai_api_key else "deterministic"
        return explicit

    configured = settings.agent_generation_method.lower()
    if configured == "openai":
        return "openai" if settings.openai_api_key else "deterministic"
    if configured == "deterministic":
        return "deterministic"
    return "openai" if settings.openai_api_key else "deterministic"
