# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MetricChat — an AI-powered analytics agent for your data stack (AGPL-3.0). Users chat with their data, build dashboards, manage AI rules/instructions, with memory and observability. Supports multiple LLMs (OpenAI, Anthropic, Gemini, Ollama) and data warehouses (Snowflake, BigQuery, Postgres, Redshift).

## Tech Stack

- **Backend:** Python 3.12+ / FastAPI / SQLAlchemy 2.0 (async) / Alembic / Pydantic
- **Frontend:** Nuxt 3 (SPA, SSR disabled) / Vue 3 / TypeScript / Nuxt UI / ECharts / Yarn 1.22.22
- **Database:** PostgreSQL 16 (production), SQLite (development)
- **Infrastructure:** Docker, Docker Compose, Kubernetes (Helm), Caddy reverse proxy

## Development Commands

### Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements_versioned.txt
alembic upgrade head
python main.py                              # http://localhost:8000, API docs at /docs
```

### Frontend
```bash
cd frontend
yarn install
yarn dev                                    # http://localhost:3000, proxies /api/* to :8000
yarn build                                  # production build
```

### Testing
```bash
# Backend (from backend/)
pytest -s -m e2e --db=sqlite                # end-to-end tests
pytest -s -m e2e --db=postgres              # e2e with testcontainers PostgreSQL
pytest -s -m unit --db=sqlite               # unit tests
pytest -s -m ai --db=sqlite                 # AI agent tests (needs OPENAI_API_KEY_TEST)

# Frontend (from frontend/)
npx playwright test                         # all e2e tests
npx playwright test auth                    # single test file
npx playwright test --headed                # with browser visible
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Docker
```bash
docker compose up -d                        # production (Postgres + Caddy SSL)
docker compose -f docker-compose.dev.yaml up -d  # development (no SSL)
```

## Architecture

### Backend (`backend/app/`)

**Request flow:** `routes/` → `dependencies.py` (auth, db session) → `services/` → `models/` (ORM) / `data_sources/` (external) → `schemas/` (serialize) → response. Optional SSE streaming via `streaming/` or WebSocket via `websocket_manager.py`.

**Module boundaries (unidirectional):** routes → services → models. Services never import from routes. Schemas are pure I/O contracts with no DB awareness.

Key directories:
- `ai/` — Agent orchestration, tools, planners, LLM providers, context system
- `ai/agent_v2.py` — Primary agent orchestrator (planning loop, tool execution, SSE events)
- `ai/agents/planner/` — PlannerV2 streams LLM tokens, builds decisions incrementally
- `ai/tools/implementations/` — Tool implementations (answer_question, create_widget, create_data, etc.)
- `ai/llm/clients/` — Provider-specific LLM clients behind unified `LLM` wrapper
- `ai/context/` — ContextHub builds static + warm context sections per iteration
- `core/` — Auth (fastapi-users/JWT), permissions (`@requires_permission`), parsers (dbt, LookML, Tableau)
- `settings/` — Config management, `metricchat-config.yaml` schema, environment-specific settings
- `ee/` — Enterprise features (audit, licensing)

### Frontend (`frontend/`)

**Data flow:** `pages/` / `components/` → `composables/` (esp. `useMyFetch`) → HTTP to `/api/*` (proxied to FastAPI) or WebSocket to `/ws/api`.

Key patterns:
- `useMyFetch.ts` — Centralized fetch; auto-injects org header and JWT, handles streaming
- `useOrganization.ts` / `usePermissions.ts` — Session and RBAC context
- `middleware/auth.global.ts` → `permissions.global.ts` → `onboarding.global.ts` (execution order)
- SSR is disabled; all routing is client-side via Nuxt file-based routing
- Auth via `@sidebase/nuxt-auth` with local provider (JWT in cookies, auto-refresh on window focus)
- Charts: nuxt-echarts with 16+ chart types lazy-loaded

### Agent Execution Flow

```
POST /api/reports/{id}/completions
  → completion_service → AgentV2
    → Loop (N iterations):
      → ContextHub refreshes warm context
      → PlannerV2 streams tokens → builds PlannerDecision
      → If analysis_complete: emit final answer
      → Else: ToolRegistry resolves tool → ToolRunner executes with retry/timeout
      → Capture observation, persist snapshot, emit SSE events
    → Final snapshot, title generation
  → SSE events back to client (block.upsert, tool.finished, etc.)
```

## Key Environment Variables

- `MC_DATABASE_URL` — PostgreSQL or SQLite connection string
- `MC_ENCRYPTION_KEY` — Fernet key (generate: `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
- `ENVIRONMENT` — development | staging | production
- `TESTING=true` — set during tests
- `OPENAI_API_KEY_TEST` — required for AI tests

## Important Notes

- All database operations are async (`AsyncSession` with `await`)
- Tests use NullPool and `PRAGMA busy_timeout=30000` for SQLite concurrency
- SQLite test DBs are isolated per process: `db/test_{pid}_{uuid}.db`
- Frontend proxy: `/api/*` → `http://127.0.0.1:8000`, `/ws/api` → `ws://127.0.0.1:8000`
- `MC_ENCRYPTION_KEY` must be persistent in production (users logged out on container restart otherwise)
- Domain exceptions are raised in services and mapped to HTTP errors at the route layer
