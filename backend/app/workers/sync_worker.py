from app.models import APIModel


class WorkerRunResult(APIModel):
    worker_name: str
    status: str
    message: str


def run_once() -> WorkerRunResult:
    return WorkerRunResult(
        worker_name="sync-worker",
        status="skipped",
        message="External syncs are disabled until integrations are configured.",
    )

