# GrantPilot Infrastructure

This folder contains service definitions and integration notes for the systems GrantPilot will use after demo mode.

- `clickhouse/schema.sql`: target analytical database schema
- `airbyte/`: source sync planning
- `composio/`: authenticated tool execution planning
- `guild/`: experiment tracking scaffold
- `openui/`: UI prototyping notes

The running application currently uses local mock storage. These files establish the deployment and data architecture without enabling external side effects.

