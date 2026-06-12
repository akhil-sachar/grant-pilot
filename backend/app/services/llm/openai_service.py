from __future__ import annotations

import json
import logging
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI chat completions with optional Langfuse tracing."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._client: Any | None = None
        self._langfuse: Any | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.settings.openai_api_key)

    @property
    def langfuse_enabled(self) -> bool:
        return bool(
            self.settings.langfuse_enabled
            and self.settings.langfuse_public_key
            and self.settings.langfuse_secret_key
        )

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.enabled:
            raise RuntimeError("OpenAI is not configured. Set OPENAI_API_KEY.")

        if self.langfuse_enabled:
            import os

            os.environ.setdefault("LANGFUSE_PUBLIC_KEY", self.settings.langfuse_public_key)
            os.environ.setdefault("LANGFUSE_SECRET_KEY", self.settings.langfuse_secret_key)
            os.environ.setdefault("LANGFUSE_HOST", self.settings.langfuse_host)
            from langfuse.openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        else:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def _get_langfuse(self) -> Any | None:
        if not self.langfuse_enabled:
            return None
        if self._langfuse is None:
            from langfuse import get_client

            self._langfuse = get_client()
        return self._langfuse

    def chat_json(
        self,
        *,
        agent_name: str,
        action: str,
        system_prompt: str,
        user_prompt: str,
        metadata: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("OpenAI is not configured.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        trace_metadata = {"agent_name": agent_name, "action": action, **(metadata or {})}

        langfuse = self._get_langfuse()
        if langfuse is not None:
            with langfuse.start_as_current_observation(
                as_type="generation",
                name=f"{agent_name}:{action}",
                model=self.settings.openai_model,
                metadata=trace_metadata,
                input={"system": system_prompt, "user": user_prompt},
            ) as generation:
                response = self._get_client().chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or "{}"
                parsed = json.loads(content)
                generation.update(output=parsed)
                return parsed

        response = self._get_client().chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def chat_text(
        self,
        *,
        agent_name: str,
        action: str,
        system_prompt: str,
        user_prompt: str,
        metadata: dict[str, Any] | None = None,
        temperature: float = 0.3,
    ) -> str:
        if not self.enabled:
            raise RuntimeError("OpenAI is not configured.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        trace_metadata = {"agent_name": agent_name, "action": action, **(metadata or {})}

        langfuse = self._get_langfuse()
        if langfuse is not None:
            with langfuse.start_as_current_observation(
                as_type="generation",
                name=f"{agent_name}:{action}",
                model=self.settings.openai_model,
                metadata=trace_metadata,
                input={"system": system_prompt, "user": user_prompt},
            ) as generation:
                response = self._get_client().chat.completions.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    temperature=temperature,
                )
                content = response.choices[0].message.content or ""
                generation.update(output=content)
                return content.strip()

        response = self._get_client().chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()


_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
