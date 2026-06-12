from app.config import Settings
from app.services.composio_service import ComposioService, get_composio_service


class ComposioIntegration:
    """Legacy adapter boundary — delegates to ComposioService."""

    def __init__(self, settings: Settings):
        self._service = get_composio_service()
        self.api_key = settings.composio_api_key
        self.enabled = self._service.mode.value == "live"

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError(
                "Composio live mode is not enabled. Set COMPOSIO_API_KEY and disable DEMO_MODE."
            )

    @property
    def service(self) -> ComposioService:
        return self._service
