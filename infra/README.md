# GrantPilot Infrastructure

This folder contains service definitions and integration notes for the systems GrantPilot uses.

- `clickhouse/schema.sql`: analytical database schema
- `composio/`: authenticated tool execution planning
- `guild/`: experiment tracking scaffold
- `openui/`: UI prototyping notes

The running application uses ClickHouse with local mock fallback. Funding sources are ingested directly via built-in adapters.
