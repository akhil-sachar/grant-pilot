# GrantPilot

GrantPilot is an autonomous scholarship and grant application agent for hackathon demos. Six agents discover opportunities, match funding, improve essays, draft recommendations, generate outreach, and create notifications — with Guild AI observability, OpenUI dynamic layouts, and Composio integrations.

## Stack

- **Frontend:** Next.js 15, React, TypeScript, Tailwind CSS
- **Backend:** Python FastAPI
- **Storage:** ClickHouse (primary) with local JSON mock fallback
- **Integrations:** Airbyte, Composio, Guild AI, OpenUI, Render

## Quick start (demo mode)

Demo mode works without ClickHouse or external API keys. The frontend uses rich mock data; the backend runs real agents against local storage.

### 1. Environment

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

Ensure these are set (defaults in `.env.example`):

```bash
DEMO_MODE=true
NEXT_PUBLIC_DEMO_MODE=true
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
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

### 4. Trigger agents manually (optional)

With the API running:

```bash
# Full demo pipeline (all agents in sequence)
curl -X POST http://localhost:8000/api/v1/demo/run

# Individual agents
curl -X POST http://localhost:8000/api/v1/sponsor/scan
curl -X POST http://localhost:8000/api/v1/matching/run
curl -X POST http://localhost:8000/api/v1/notifications/run

# Health check
curl http://localhost:8000/health
```

API docs: **http://localhost:8000/docs**

## Full local setup (with ClickHouse)

1. Start ClickHouse:

```bash
docker compose up -d clickhouse
```

2. Set in `.env` / `backend/.env`:

```bash
CLICKHOUSE_ENABLED=true
CLICKHOUSE_FALLBACK_ENABLED=true
CLICKHOUSE_HOST=localhost
```

3. Initialize storage:

```bash
curl -X POST http://localhost:8000/api/v1/storage/initialize
curl -X POST http://localhost:8000/api/v1/storage/sample-data
```

4. Run frontend and backend as above.

Background workers start automatically with the API:
- **SponsorAgent** — periodic funding scans (`SPONSOR_SCAN_INTERVAL_SECONDS`, default 300)
- **NotificationAgent** — periodic notification generation (`NOTIFICATION_SCAN_INTERVAL_SECONDS`, default 180)

## Deploy on Render

The repo includes `render.yaml` for one-click Blueprint deploy:

1. Push to GitHub and connect the repo in [Render](https://render.com).
2. Use **New → Blueprint** and select `render.yaml`.
3. Render creates:
   - **grantpilot-api** — FastAPI (`/health` check)
   - **grantpilot-web** — Next.js (`/` check)
4. Env vars are wired in the blueprint (`DEMO_MODE`, `NEXT_PUBLIC_DEMO_MODE`, Guild AI, schedulers, CORS).

After deploy, open the web service URL and go to `/demo` for the showcase.

## Project layout

```txt
grant-pilot/
  frontend/              Next.js app (pages, OpenUI renderer, demo UI)
  backend/               FastAPI app, agents, services, workers
  infra/                 ClickHouse schema, integration notes
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

All runs are logged to `AgentActionLog`, tracked by **Guild AI**, and traced in **Langfuse** when configured.

## AI agents (OpenAI + Langfuse)

When `OPENAI_API_KEY` is set, all six agents use OpenAI (`gpt-4o-mini` by default):

| Agent | OpenAI action | Langfuse trace name |
|-------|---------------|---------------------|
| SponsorAgent | Enrich opportunity descriptions | `sponsor-agent:enrich_opportunity` |
| MatchingAgent | Score fit vs profile | `matching-agent:score_opportunity` |
| EssayAgent | Tailor essays | `essay-agent:improve_essay` |
| RecommendationAgent | Draft recommendation letters | `recommendation-agent:generate_recommendation` |
| OutreachAgent | Write outreach emails | `outreach-agent:generate_outreach` |
| NotificationAgent | Polish notification copy | `notification-agent:enhance_notification` |

Set `AGENT_GENERATION_METHOD=auto` (default) to use OpenAI when the key is present, or `deterministic` to force rule-based logic.

If OpenAI fails, agents fall back to deterministic generators automatically.

## Key API routes

- `GET /health` — liveness
- `GET /api/v1/config` — runtime and integration flags (OpenAI, Langfuse, Composio)
- `GET /api/v1/dashboard` — metrics and ranked opportunities
- `GET /api/v1/agent-activity` — runtime, success rate, Guild logs
- `GET /api/v1/openui/layout` — dynamic UI component tree
- `POST /api/v1/demo/run` — full demo pipeline (requires `DEMO_MODE=true`)
- `GET /api/v1/composio/status` — Composio simulated vs live mode

Full CRUD under `/api/v1` for documents, opportunities, matches, applications, notifications, and agent actions.

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Enables OpenAI for all agents |
| `OPENAI_MODEL` | Model name (default `gpt-4o-mini`) |
| `AGENT_GENERATION_METHOD` | `auto`, `openai`, or `deterministic` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key |
| `LANGFUSE_HOST` | Langfuse API host (default cloud) |
| `LANGFUSE_ENABLED` | Toggle Langfuse tracing |
| `DEMO_MODE` | Backend demo flag; enables `/demo/run` |
| `NEXT_PUBLIC_DEMO_MODE` | Frontend uses mock API data when `true` |
| `GUILD_AI_ENABLED` | Track agent runs in Guild AI |
| `OPENUI_ENABLED` | Serve OpenUI layout specs |
| `DEMO_AUTO_RUN` | Run demo pipeline on API startup |
| `COMPOSIO_API_KEY` | Live Composio (simulated if unset) |
| `SPONSOR_SCAN_ENABLED` | Background opportunity scans |
| `NOTIFICATION_SCAN_ENABLED` | Background notification scans |

See `.env.example` for the full list.

## Database

ClickHouse DDL: `infra/clickhouse/schema.sql`. Tables are also created at startup via `ClickHouseService`.
