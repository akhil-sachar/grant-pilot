from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.repository import get_repository  # noqa: E402


def main() -> None:
    repository = get_repository()
    repository.initialize()
    ingestion_run = repository.load_sample_data()
    print(
        f"Loaded {ingestion_run.records_loaded}/{ingestion_run.records_seen} "
        f"sample records into {repository.storage_mode} storage."
    )


if __name__ == "__main__":
    main()

