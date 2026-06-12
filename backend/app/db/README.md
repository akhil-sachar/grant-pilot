# Storage

GrantPilot uses ClickHouse as the primary storage and analytics layer when it is available. If ClickHouse cannot be reached, the repository falls back to file-backed mock storage.

- Seed data is defined in `seed_data.py`.
- Runtime mock data is written to `backend/.data/mock_storage.json`.
- Production-oriented ClickHouse DDL is in `infra/clickhouse/schema.sql`.
- `clickhouse_service.py` owns table creation and ClickHouse serialization.
- `repository.py` owns the repository pattern and fallback behavior.

Load sample data:

```bash
python backend/scripts/load_sample_data.py
```

Or call:

```bash
POST /api/v1/storage/sample-data
```
