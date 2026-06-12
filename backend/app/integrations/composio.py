from app.config import Settings


class ComposioIntegration:
    def __init__(self, settings: Settings):
        self.api_key = settings.composio_api_key
        self.enabled = bool(settings.composio_api_key) and not settings.demo_mode

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Composio integration is not configured or demo mode is active.")

