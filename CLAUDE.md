# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MetricChat — an AI-powered analytics agent for your data stack (AGPL-3.0). Users chat with their data, build dashboards, manage AI rules/instructions, with memory and observability. Supports multiple LLMs (OpenAI, Anthropic, Gemini, Ollama) and data warehouses (Snowflake, BigQuery, Postgres, Redshift, DuckDB, Databricks, ClickHouse, and 25+ others).

## Tech Stack

- **Backend:** Python 3.12+ / FastAPI / SQLAlchemy 2.0 (async) / Alembic / Pydantic
- **Frontend:** Nuxt 3 (SPA, SSR disabled) / Vue 3 / TypeScript / Nuxt UI / ECharts / Yarn 1.22.22
- **Database:** PostgreSQL 16 (production), SQLite (development)
- **Infrastructure:** Docker, Docker Compose, Kubernetes (Helm), Caddy reverse proxy
- **Key frontend deps:** ag-grid-vue3, gridstack, vue-flow, nuxt-tiptap-editor, monaco-editor, @sidebase/nuxt-auth, @nuxt-alt/proxy

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
pytest -s -m e2e --db=sqlite tests/e2e/test_report.py              # single file
pytest -s -m e2e --db=sqlite tests/e2e/test_report.py::test_name   # single test

# Frontend (from frontend/)
npx playwright test                         # all e2e tests
npx playwright test auth                    # single test file
npx playwright test --headed                # with browser visible
```

Test fixtures live in `tests/fixtures/` and are auto-imported via `conftest.py`. Each test function gets fresh migrations (per-function isolation). No linter or formatter is configured for either backend or frontend.

```bash
# Frontend type-checking (from frontend/)
npx vue-tsc --noEmit                       # strict type check (stricter than yarn build)
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
- `ai/agents/` — Specialized agents: planner, answer, coder, dashboard_designer, data_source, doc, excel, judge, reporter, suggest_instructions
- `ai/tools/implementations/` — 17 tool implementations (answer_question, create_widget, create_data, etc.)
- `ai/tools/mcp/` — Model Context Protocol server integration (11 modules)
- `ai/llm/clients/` — Provider-specific LLM clients behind unified `LLM` wrapper
- `ai/context/` — ContextHub builds static + warm context; `builders/` (15 modules), `sections/` (16 modules)
- `ai/code_execution/` — Sandboxed code execution for agent tools
- `core/` — Auth (fastapi-users/JWT), permissions (`@requires_permission`), parsers (dbt, LookML, Tableau, sqlx, markdown), scheduler (APScheduler), telemetry
- `data_sources/clients/` — 33+ database/service connectors (Snowflake, BigQuery, Redshift, Postgres, DuckDB, Databricks, ClickHouse, Athena, Azure Data Explorer, Tableau, PowerBI, Salesforce, etc.)
- `routes/` — 43 route modules covering all API endpoints
- `services/` — 57+ service modules; key ones: completion_service, console_service, data_source_service, build_service
- `schemas/` — Pydantic request/response types; subdirs `ai/` and `datasources/`
- `serializers/` — Response shaping/normalization
- `settings/` — Config management, `metricchat-config.yaml` schema, environment-specific settings
- `ee/` — Enterprise features (audit, licensing)

### Frontend (`frontend/`)

**Data flow:** `pages/` / `components/` → `composables/` (esp. `useMyFetch`) → HTTP to `/api/*` (proxied to FastAPI) or WebSocket to `/ws/api`.

Key directories:
- `types/` — Shared TypeScript interfaces (completion.ts, report.ts)
- `composables/` — Reusable state/logic: useMyFetch, useOrganization, usePermissions, useOnboarding, useDomain, useInstructions, useSharedFilters, useSidebar, useAuthenticatedImage, useOrgSettings
- `components/dashboard/` — Dashboard widget system (ArtifactFrame, FilterBuilder, FullscreenGrid, SlideViewer, themes, charts, table, KPI, text widgets, block registry)
- `layouts/` — 7 layouts: default (main nav wrapper), data, excel, monitoring, onboarding, settings, users
- `plugins/` — Client-only: vue-draggable-resizable, vue-flow, gridstack CSS, fetchPermissions
- `pages/` — Routes: index (dashboard), data, reports, queries, files, monitoring, evals, integrations, onboarding, organizations, settings, users, excel, r/[id] (public reports)
- `ee/` — Enterprise features (separate components and composables)

Key patterns:
- `useMyFetch.ts` — Centralized fetch; auto-injects org header and JWT, handles streaming
- `useOrganization.ts` / `usePermissions.ts` — Session and RBAC context
- `middleware/auth.global.ts` → `permissions.global.ts` → `onboarding.global.ts` (execution order)
- SSR is disabled; all routing is client-side via Nuxt file-based routing
- Auth via `@sidebase/nuxt-auth` with local provider (JWT in cookies, auto-refresh on window focus). Session data from `/users/whoami` is untyped — cast `currentUser.value` when accessing user fields like `id`, `email`
- Charts: nuxt-echarts with 16+ chart types lazy-loaded
- Nuxt UI theme: primary=teal, gray=stone (configured in `app.config.ts`)
- Dual report routes: `/reports/[id]` (authenticated editor) and `/r/[id]` (public/published view)

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

## Configuration

- `metricchat.yaml` at project root — base config
- `configs/` — Variants: `metricchat.dev.yaml`, `metricchat.multiorg.dev.yaml`, `metricchat.google_oauth.yaml`
- Config sections: base_url, features (signups, multi-org, email verification), auth (hybrid | local_only | sso_only), google_oauth, OIDC providers, intercom, telemetry, license
- Config module: `backend/app/settings/app_config.py` (class `AppConfig`)

## CI/CD

- `.github/workflows/`: e2e-tests.yml, docker-image.yml, release.yml, integrations.yml, ds-integrations.yml, helm-publish.yaml
- Test matrix runs SQLite and PostgreSQL variants
- AI tests trigger conditionally on changes to `backend/app/ai/**`
- Docker images: `metricchat/metricchat`
- Helm chart in `k8s/chart/`

## Important Notes

- All database operations are async (`AsyncSession` with `await`)
- Tests use NullPool and `PRAGMA busy_timeout=30000` for SQLite concurrency
- SQLite test DBs are isolated per process: `db/test_{pid}_{uuid}.db`
- Frontend proxy: `/api/*` → `http://127.0.0.1:8000`, `/ws/api` → `ws://127.0.0.1:8000`, `/mcp` → `/api/mcp`
- `MC_ENCRYPTION_KEY` must be persistent in production (users logged out on container restart otherwise)
- Domain exceptions are raised in services and mapped to HTTP errors at the route layer
- AGENTS.md files exist in `backend/`, `frontend/`, and `k8s/` with module-specific guidance
- `frontend/types/` contains shared TypeScript interfaces — add new types here, not inline
