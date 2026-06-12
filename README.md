# GrantPilot

GrantPilot is a hackathon foundation for an autonomous scholarship and grant application agent. This scaffold focuses on architecture, contracts, mock storage, and responsive product surfaces. Agent logic is intentionally not implemented yet.

## Stack

- Frontend: Next.js 15, React, TypeScript, Tailwind CSS
- Backend: Python FastAPI
- Infrastructure targets: ClickHouse, Airbyte, Composio, Guild AI, OpenUI, Render
- Current storage mode: ClickHouse primary with local mock fallback

## Project Layout

```txt
grant-pilot/
  frontend/          Next.js app router UI
  backend/           FastAPI app, models, repositories, services, routes, integrations
  infra/             ClickHouse schema and integration notes
  docker-compose.yml Local ClickHouse service
  render.yaml        Render deployment blueprint
```

## Local Setup

1. Copy environment files:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

2. Install frontend dependencies:

```bash
npm --prefix frontend install
```

3. Install backend dependencies in your Python environment:

```bash
pip install -r backend/requirements.txt
```

4. Run the services in separate terminals:

```bash
npm --prefix frontend run dev
uvicorn app.main:app --app-dir backend --reload
```

Frontend runs on `http://localhost:3000`. Backend runs on `http://localhost:8000`.

## Storage And Demo Mode

GrantPilot now attempts to use ClickHouse as the primary storage layer when `CLICKHOUSE_ENABLED=true`. If ClickHouse is unavailable and `CLICKHOUSE_FALLBACK_ENABLED=true`, the API falls back to local mock JSON storage.

- `NEXT_PUBLIC_DEMO_MODE=true` makes the frontend use local mock data.
- `CLICKHOUSE_ENABLED=true` makes the backend initialize ClickHouse tables.
- `CLICKHOUSE_FALLBACK_ENABLED=true` preserves local fallback storage.
- `MOCK_STORAGE_PATH=backend/.data/mock_storage.json` controls the fallback path.

Start ClickHouse locally:

```bash
docker compose up -d clickhouse
```

Initialize storage or load sample data:

```bash
curl -X POST http://localhost:8000/api/v1/storage/initialize
curl -X POST http://localhost:8000/api/v1/storage/sample-data
```

## API Surface

The backend exposes versioned routes under `/api/v1`:

- `GET /api/v1/dashboard`
- `GET /api/v1/dashboard/analytics`
- `GET | PUT /api/v1/profile/me`
- CRUD `/api/v1/documents`
- CRUD `/api/v1/opportunities`
- CRUD `/api/v1/matches`
- CRUD `/api/v1/applications`
- CRUD `/api/v1/essay-versions`
- CRUD `/api/v1/recommendation-drafts`
- CRUD `/api/v1/outreach-emails`
- CRUD `/api/v1/notifications`
- CRUD `/api/v1/agent-actions`
- CRUD `/api/v1/ingestion-runs`
- `GET /api/v1/storage/health`
- `POST /api/v1/storage/initialize`
- `POST /api/v1/storage/sample-data`
- `GET /api/v1/applications/{application_id}`

## Database Schemas

ClickHouse DDL lives in `infra/clickhouse/schema.sql`. The backend also creates tables automatically through `ClickHouseService` at startup.

## Not Implemented Yet

- AI agents and autonomous workflows
- Document parsing and embedding
- Real ClickHouse persistence
- Airbyte sync jobs
- Composio tool execution
- Guild AI experiments
- OpenUI prompt-to-interface workflows
