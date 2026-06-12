"""Shared OpenAI + Langfuse integration for GrantPilot agents."""

from app.services.llm.agent_method import resolve_generation_method
from app.services.llm.openai_service import OpenAIService, get_openai_service

__all__ = [
    "OpenAIService",
    "get_openai_service",
    "resolve_generation_method",
]
