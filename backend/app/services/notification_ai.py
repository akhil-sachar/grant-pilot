from __future__ import annotations

from app.services.llm.openai_service import get_openai_service


def enhance_notification_copy(
    *,
    title: str,
    message: str,
    notification_type: str,
    context: dict,
) -> tuple[str, str]:
    """Polish notification title and message with OpenAI."""
    llm = get_openai_service()
    if not llm.enabled:
        return title, message

    try:
        data = llm.chat_json(
            agent_name="notification-agent",
            action="enhance_notification",
            system_prompt=(
                "Rewrite student notifications to be clear, actionable, and concise. "
                "Return JSON: title (string), message (string). Keep facts accurate."
            ),
            user_prompt=(
                f"Type: {notification_type}\n"
                f"Current title: {title}\n"
                f"Current message: {message}\n"
                f"Context: {context}"
            ),
        )
        return (
            str(data.get("title", title)),
            str(data.get("message", message)),
        )
    except Exception:
        return title, message
