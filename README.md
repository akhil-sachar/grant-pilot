# GrantPilot

GrantPilot is an autonomous scholarship and grant application agent. Six agents discover opportunities, match funding, improve essays, draft recommendations, generate outreach, and create notifications — with Guild AI observability, OpenUI dynamic layouts, OpenAI + Langfuse, and Composio integrations.

## Stack

- **Frontend:** Next.js 15, React, TypeScript, Tailwind CSS
- **Backend:** Python FastAPI
- **Storage:** ClickHouse (primary) with local JSON mock fallback
- **Funding sources:** Built-in adapters + live [Grants.gov search2 API](https://www.grants.gov/api/common/search2)
- **Integrations:** OpenAI, Langfuse, Composio, Guild AI, OpenUI, Render

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ (3.12 recommended)
- **Docker** (optional, for local ClickHouse)

## Quick start (demo mode)

Demo mode works without ClickHouse or API keys. The frontend uses rich mock data; the backend runs agents against local storage.

### 1. Environment

Copy env templates. **Backend config lives in `backend/.env`** (this is what the API reads):

```bash
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

Minimum settings:

```bash
# backend/.env
DEMO_MODE=true
CLICKHOUSE_FALLBACK_ENABLED=true

# frontend/.env.local
NEXT_PUBLIC_DEMO_MODE=true
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Windows (PowerShell):**

```powershell
Copy-Item frontend\.env.example frontend\.env.local
Copy-Item backend\.env.example backend\.env
```

### 2. Install dependencies

```bash
npm --prefix frontend install
pip install -r backend/requirements.txt
```

### 3. Run (two terminals)

**Terminal 1 — API**

```bash
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend**

```bash
npm --prefix frontend run dev
```

Open **http://localhost:3000**

| Page | URL | What it shows |
|------|-----|----------------|
| Hackathon demo | `/demo` | One-click full agent pipeline |
| Agent Activity | `/agents` | Guild AI metrics + OpenUI layout |
| Dashboard | `/dashboard` | Ranked matches and pipeline |
| Opportunities | `/opportunities` | SponsorAgent scan status |
| Applications | `/applications` | Essay, recommendation, outreach editors |
| Notifications | `/notifications` | Notification Center |

### 4. Trigger agents (optional)

```bash
# Full demo pipeline (all agents in sequence)
curl -X POST http://localhost:8000/api/v1/demo/run

# Individual agents
curl -X POST http://localhost:8000/api/v1/sponsor/scan
curl -X POST http://localhost:8000/api/v1/matching/run
curl -X POST http://localhost:8000/api/v1/notifications/run

# Check health and integration flags
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/config
```

API docs: **http://localhost:8000/docs**

## Live backend mode

To use the real API (OpenAI, ClickHouse, Grants.gov scans) instead of frontend mocks:

1. Add keys to `backend/.env` (see [Environment variables](#environment-variables))
2. Set in `frontend/.env.local`:

```bash
NEXT_PUBLIC_DEMO_MODE=false
```

3. Restart both servers.

With `OPENAI_API_KEY` set and `AGENT_GENERATION_METHOD=auto`, all six agents use OpenAI and fall back to deterministic logic on failure.

**Composio live mode** requires both `COMPOSIO_API_KEY` and `DEMO_MODE=false`.

## Opportunity discovery

SponsorAgent scans funding through **source adapters** (no external sync pipeline):

| Source | Data |
|--------|------|
| `grants_gov` | Live federal grants via Grants.gov search2 (no auth) |
| `nsf`, `nih`, `sbir_sttr`, `yc_grants`, `foundation_directories`, `university_grants`, `scholarships`, `corporate_innovation` | Embedded demo records (ready for live API wiring) |

Configure Grants.gov in `backend/.env`:

```bash
GRANTS_GOV_LIVE_ENABLED=true
GRANTS_GOV_API_URL=https://api.grants.gov/v1/api/search2
GRANTS_GOV_SEARCH_KEYWORD=education scholarship student
GRANTS_GOV_OPP_STATUSES=forecasted|posted
GRANTS_GOV_SEARCH_ROWS=25
```

Trigger a scan from the Opportunities page (**Scan now**) or `POST /api/v1/sponsor/scan`. Scan status: `GET /api/v1/sponsor/status`.

## ClickHouse setup

ClickHouse stores profiles, opportunities, matches, applications, agent logs, notifications, and more. If unavailable, the app falls back to `backend/.data/mock_storage.json`.

### Local Docker

```bash
docker compose up -d clickhouse
```

Default local credentials (from `docker-compose.yml`):

```bash
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=grantpilot
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=          # empty for local Docker
```

**Important:** use `grantpilot` as the database name (no spaces).

### Cloud ClickHouse

Use the host, user, and password from your provider's connection string (e.g. [ClickHouse Cloud](https://clickhouse.cloud) → Connect).

### Initialize data

After the API is running:

```bash
curl -X POST http://localhost:8000/api/v1/storage/initialize
curl -X POST http://localhost:8000/api/v1/storage/sample-data
```

Check storage: `GET /api/v1/storage/health`

### Verify integrations

```bash
cd backend
python scripts/check_integrations.py
```

## Background workers

These start automatically with the API:

- **SponsorAgent** — periodic funding scans (`SPONSOR_SCAN_INTERVAL_SECONDS`, default 300)
- **NotificationAgent** — periodic notifications (`NOTIFICATION_SCAN_INTERVAL_SECONDS`, default 180)

## Deploy on Render

The repo includes `render.yaml` for Blueprint deploy:

1. Push to GitHub and connect the repo in [Render](https://render.com).
2. **New → Blueprint** → select `render.yaml`.
3. Render creates:
   - **grantpilot-api** — FastAPI (`/health`)
   - **grantpilot-web** — Next.js (`/`)
4. Set secrets in the Render dashboard: `OPENAI_API_KEY`, `LANGFUSE_*`, `COMPOSIO_API_KEY` (optional).

Render runs with `CLICKHOUSE_ENABLED=false` and mock JSON fallback by default. Add a ClickHouse service and env vars for persistent production storage.

After deploy, open the web URL and go to `/demo`.

## Project layout

```txt
grant-pilot/
  frontend/              Next.js app (OpenUI renderer, demo UI)
  backend/               FastAPI app, agents, services, workers
    app/agents/          Six autonomous agents
    app/adapters/funding/  Funding source adapters + Grants.gov client
    scripts/             Utilities (check_integrations.py, load_sample_data.py)
  infra/clickhouse/      ClickHouse DDL
  docker-compose.yml     Local ClickHouse
  render.yaml            Render deployment blueprint
```

## Agents

| Agent | Trigger | Purpose |
|-------|---------|---------|
| SponsorAgent | `POST /api/v1/sponsor/scan` | Discover funding opportunities |
| MatchingAgent | `POST /api/v1/matching/run` | Score opportunities vs profile |
| EssayAgent | `POST /api/v1/applications/{id}/improve-essay` | Tailor essays per opportunity |
| RecommendationAgent | `POST /api/v1/applications/{id}/generate-recommendation` | Draft recommender letters |
| OutreachAgent | `POST /api/v1/applications/{id}/generate-outreach` | Personalized emails + Composio |
| NotificationAgent | `POST /api/v1/notifications/run` | Actionable notifications |

All runs are logged to `AgentActionLog`, tracked by **Guild AI** (`.guild/runs.jsonl`), and traced in **Langfuse** when configured.

## OpenAI + Langfuse

When `OPENAI_API_KEY` is set:

| Agent | OpenAI action | Langfuse trace |
|-------|---------------|----------------|
| SponsorAgent | Enrich opportunity descriptions | `sponsor-agent:enrich_opportunity` |
| MatchingAgent | Score fit vs profile | `matching-agent:score_opportunity` |
| EssayAgent | Tailor essays | `essay-agent:improve_essay` |
| RecommendationAgent | Draft recommendation letters | `recommendation-agent:generate_recommendation` |
| OutreachAgent | Write outreach emails | `outreach-agent:generate_outreach` |
| NotificationAgent | Polish notification copy | `notification-agent:enhance_notification` |

Set `AGENT_GENERATION_METHOD=auto` (default), `openai`, or `deterministic`.

## Key API routes

| Route | Description |
|-------|-------------|
| `GET /health` | Liveness |
| `GET /api/v1/config` | Runtime and integration flags |
| `GET /api/v1/dashboard` | Metrics and ranked opportunities |
| `GET /api/v1/agent-activity` | Agent metrics and Guild logs |
| `GET /api/v1/openui/layout` | Dynamic UI component tree |
| `GET /api/v1/sponsor/status` | Sponsor scan status |
| `POST /api/v1/demo/run` | Full demo pipeline (`DEMO_MODE=true`) |
| `GET /api/v1/composio/status` | Composio simulated vs live |

Full CRUD under `/api/v1` for documents, opportunities, matches, applications, notifications, and agent actions.

## Environment variables

| Variable | Description |
|----------|-------------|
| `DEMO_MODE` | Backend demo flag; enables `/demo/run` |
| `NEXT_PUBLIC_DEMO_MODE` | Frontend uses mock data when `true` |
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL for the frontend |
| `OPENAI_API_KEY` | Enables OpenAI for all agents |
| `OPENAI_MODEL` | Model name (default `gpt-4o-mini`) |
| `AGENT_GENERATION_METHOD` | `auto`, `openai`, or `deterministic` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_HOST` | Langfuse host (default cloud) |
| `LANGFUSE_ENABLED` | Toggle Langfuse tracing |
| `COMPOSIO_API_KEY` | Live Composio (simulated if unset) |
| `CLICKHOUSE_ENABLED` | Use ClickHouse as primary storage |
| `CLICKHOUSE_FALLBACK_ENABLED` | Fall back to mock JSON if ClickHouse fails |
| `CLICKHOUSE_HOST` | ClickHouse host |
| `CLICKHOUSE_PORT` | ClickHouse HTTP port (default 8123) |
| `CLICKHOUSE_DATABASE` | Database name (`grantpilot`) |
| `CLICKHOUSE_USER` | ClickHouse user (default `default`) |
| `CLICKHOUSE_PASSWORD` | ClickHouse password (empty for local Docker) |
| `GRANTS_GOV_LIVE_ENABLED` | Fetch live federal grants on scan |
| `GRANTS_GOV_SEARCH_KEYWORD` | Grants.gov search keyword |
| `GRANTS_GOV_OPP_STATUSES` | e.g. `forecasted\|posted` |
| `GUILD_AI_ENABLED` | Track agent runs in Guild AI |
| `OPENUI_ENABLED` | Serve OpenUI layout specs |
| `DEMO_AUTO_RUN` | Run demo pipeline on API startup |
| `SPONSOR_SCAN_ENABLED` | Background opportunity scans |
| `NOTIFICATION_SCAN_ENABLED` | Background notification scans |

See `backend/.env.example` for the full backend list and `frontend/.env.example` for frontend vars.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API fails to start with CORS parse error | Do not use a root `.env` file or directory — config loads from `backend/.env` only |
| ClickHouse connection errors | Use `CLICKHOUSE_DATABASE=grantpilot` (no spaces); local Docker password is empty |
| Composio stays simulated | Set `COMPOSIO_API_KEY` and `DEMO_MODE=false` |
| `/demo/run` returns 403 | Set `DEMO_MODE=true` in `backend/.env` |
| Frontend shows stale mock data | Set `NEXT_PUBLIC_DEMO_MODE=false` and restart the dev server |

Run `python backend/scripts/check_integrations.py` to verify ClickHouse, OpenAI, Langfuse, Composio, and Grants.gov.

## Database

ClickHouse DDL: `infra/clickhouse/schema.sql`. Tables are also created at startup via `ClickHouseService`.

Stored entities include: user profiles, documents, opportunities, match results, applications, essay versions, recommendation drafts, outreach emails, notifications, agent action logs, and ingestion runs.
