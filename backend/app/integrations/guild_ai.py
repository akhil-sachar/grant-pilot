from app.config import Settings


class GuildAIIntegration:
    def __init__(self, settings: Settings):
        self.guild_home = settings.guild_home
        self.enabled = not settings.demo_mode

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("Guild AI integration is disabled in demo mode.")

