from app.config import Settings
from app.services.airbyte_service import AirbyteService


class AirbyteIntegration:
    """Legacy adapter boundary — delegates to AirbyteService."""

    def __init__(self, settings: Settings):
        self._service = AirbyteService(settings=settings)
        self.base_url = settings.airbyte_api_url
        self.enabled = self._service.is_configured

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError(
                "Airbyte integration is not configured. Set AIRBYTE_API_KEY and AIRBYTE_WORKSPACE_ID."
            )

    @property
    def service(self) -> AirbyteService:
        return self._service
