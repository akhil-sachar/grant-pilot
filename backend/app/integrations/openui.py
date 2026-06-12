from app.config import Settings


class OpenUIIntegration:
    def __init__(self, settings: Settings):
        self.base_url = settings.openui_url
        self.enabled = settings.openui_enabled

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("OpenUI integration is disabled.")
