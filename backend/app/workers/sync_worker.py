from app.models import APIModel


class WorkerRunResult(APIModel):
    worker_name: str
    status: str
    message: str


def run_once() -> WorkerRunResult:
    import asyncio

    from app.workers.scan_scheduler import run_sponsor_scan

    return asyncio.run(run_sponsor_scan())
