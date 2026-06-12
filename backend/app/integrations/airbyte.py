from app.config import Settings


class AirbyteIntegration:
    def __init__(self, settings: Settings):
        self.base_url = settings.airbyte_api_url
        self.enabled = not settings.demo_mode

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Airbyte integration is disabled in demo mode.")

