from app.config import Settings


class ClickHouseIntegration:
    def __init__(self, settings: Settings):
        self.host = settings.clickhouse_host
        self.port = settings.clickhouse_port
        self.database = settings.clickhouse_database
        self.user = settings.clickhouse_user
        self.enabled = not settings.demo_mode

    def assert_enabled(self) -> None:
        if not self.enabled:
            raise RuntimeError("ClickHouse integration is disabled while mock storage is active.")

