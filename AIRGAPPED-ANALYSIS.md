# Airgapped Deployment Analysis

Full scan of the Bag of Words codebase for external dependencies that break in airgapped (no internet) environments.

---

## CRITICAL - Complete Feature Breakage

### 1. CDN-loaded JavaScript libraries (Artifacts completely broken)

The artifact rendering system loads **5 libraries from CDNs** at runtime. Without internet, all artifacts (charts, dashboards, React components) render as blank white pages.

| Library | CDN | Locations |
|---------|-----|-----------|
| Tailwind CSS | `cdn.tailwindcss.com` | 7 |
| React 18 | `unpkg.com/react@18` | 4 |
| ReactDOM 18 | `unpkg.com/react-dom@18` | 4 |
| Babel Standalone | `unpkg.com/@babel/standalone` | 4 |
| ECharts 5 | `cdn.jsdelivr.net/npm/echarts@5` | 4 |

**Files:**
- `frontend/public/artifact-sandbox.html:9-19`
- `frontend/pages/r/[id]/index.vue:349-376`
- `frontend/components/dashboard/ArtifactFrame.vue:947-975`
- `backend/app/services/thumbnail_service.py:270-287`
- `backend/app/ai/tools/implementations/create_artifact.py:235`

### 2. Heroicons / @nuxt/icon (UI icons missing across entire app)

849 icon references across 127+ component files. The `@nuxt/icon` module (via `@nuxt/ui`) uses a server endpoint `/_nuxt_icon` to serve icon SVGs.

In the production Docker image, only `.output/` is copied (`Dockerfile:111`), **not** `node_modules/`. If `@iconify-json/heroicons` data isn't properly inlined during build, the Nitro handler falls back to fetching from `https://api.iconify.design` -- which fails airgapped.

**Config:** `frontend/nuxt.config.ts:74-76` -- only sets `localApiEndpoint`, no explicit bundling configuration (`icon.provider`, `icon.serverBundle`, `icon.customCollections`) to force local-only icon resolution.

### 3. LLM Provider APIs (Core AI functionality broken)

| Provider | File | Endpoint |
|----------|------|----------|
| OpenAI | `backend/app/ai/llm/clients/openai_client.py` | `api.openai.com/v1` |
| Anthropic | `backend/app/ai/llm/clients/anthropic_client.py` | `api.anthropic.com` |
| Google Gemini | `backend/app/ai/llm/clients/google_client.py` | Google AI API |
| Azure OpenAI | `backend/app/ai/llm/clients/azure_client.py` | Azure endpoints |

Ollama (local LLM) is supported but there's no enforcement or detection that airgapped deployments must use a local LLM.

---

## HIGH - Authentication & Integrations Broken

### 4. OAuth/SSO login flows

- `backend/app/services/auth_providers.py:86-103` -- Google OAuth2 token exchange
- `backend/app/services/auth_providers.py:192-266` -- OIDC discovery + token exchange
- `backend/app/core/auth.py:175` -- Fetches userinfo from `https://www.googleapis.com/oauth2/v1/userinfo`

Local auth (`auth.mode: "local_only"`) works, but SSO buttons still appear if configured.

### 5. Intercom customer messaging widget

- `frontend/nuxt.config.ts:56-58` -- Hardcoded app ID: `ocwih86k`
- `frontend/layouts/default.vue:302-309` -- Boots Intercom in production
- `frontend/layouts/users.vue:10-15` -- Also initializes Intercom
- `frontend/package.json:45` -- `nuxt-3-intercom` dependency

Attempts to load `https://widget.intercom.io`. May cause console errors.

### 6. PostHog telemetry (phones home by default)

- `backend/app/core/telemetry.py:18-19` -- **Hardcoded** credentials:
  - `POSTHOG_API_KEY = "phc_aWBVqSFPK846NT5XRUm9NmiiX0ElKNDJwA97lZ3DfGq"`
  - `POSTHOG_HOST = "https://us.i.posthog.com"`
- `backend/app/settings/bow_config.py:24-25` -- Enabled by default: `enabled: bool = True`
- PostHog client initialized at module load (`telemetry.py:38`)
- 22 backend files call `telemetry.capture()` / `telemetry.identify()`

### 7. Slack & Microsoft Teams integrations

- `backend/app/services/platform_adapters/slack_adapter.py` -- 8+ API calls to `slack.com/api/*`
- `backend/app/services/platform_adapters/teams_adapter.py` -- Calls to `login.botframework.com`, `login.microsoftonline.com`, Teams API
- `backend/app/routes/slack_webhook.py`, `teams_webhook.py` -- Webhook handlers

### 8. Git operations (sync, clone, PR creation)

- `backend/app/services/git_service.py:679-715` -- `git.Repo.clone_from()` to remote URLs
- `backend/app/services/git_service.py:1251-1370` -- API calls to GitHub, GitLab, Bitbucket

### 9. Email / SMTP

- `backend/app/settings/bow_config.py:68-69` -- Default SMTP: `smtp.resend.com:587`
- `backend/app/core/auth.py:254-305` -- Password reset and verification emails

---

## MEDIUM - Data Source Connectors

All require network access to remote cloud services:

| Connector | File |
|-----------|------|
| Power BI | `backend/app/data_sources/clients/powerbi_client.py` |
| Tableau | `backend/app/data_sources/clients/tableau_client.py` |
| Salesforce | `backend/app/data_sources/clients/salesforce_client.py` |
| Google Analytics | `backend/app/data_sources/clients/google_analytics_client.py` |
| BigQuery | `backend/app/data_sources/clients/bigquery_client.py` |
| Snowflake | `backend/app/data_sources/clients/snowflake_client.py` |
| Azure Data Explorer | `backend/app/data_sources/clients/azure_data_explorer_client.py` |
| MS Fabric | `backend/app/data_sources/clients/ms_fabric_client.py` |
| Databricks | `backend/app/data_sources/clients/databricks_sql_client.py` |
| AWS Athena | `backend/app/data_sources/clients/aws_athena_client.py` |
| PostHog (data) | `backend/app/data_sources/clients/posthog_client.py` |
| GCP services | `backend/app/data_sources/clients/gcp_client.py` |

Local databases (PostgreSQL, MySQL, SQLite, DuckDB) work fine on same network.

---

## LOW - Broken Links

| Link | File |
|------|------|
| `https://bagofwords.com` | `frontend/pages/r/[id]/index.vue:71` |
| `https://bagofwords.com/pricing` | `frontend/ee/components/UpgradeBanner.vue:32` |
| `https://docs.bagofwords.com` | `frontend/layouts/default.vue` (nav menu) |
| `https://bagofwords.com/terms` | `frontend/pages/users/sign-up.vue` |
| `https://bagofwords.com/privacy` | `frontend/pages/users/sign-up.vue` |

---

## INFRASTRUCTURE - Build & Deploy Issues

### 10. Dockerfile external fetches during build

| Issue | Lines | Details |
|-------|-------|---------|
| Base images | 1, 36, 67 | `FROM ubuntu:24.04` (3 stages) |
| apt-get | 5-16, 41-48, 77-89 | Ubuntu/Microsoft package repos |
| NodeSource | 45, 80 | `curl https://deb.nodesource.com/setup_22.x` |
| Microsoft ODBC | 82-83 | `curl https://packages.microsoft.com/...` |
| pip install | 30-31 | 195 Python packages from PyPI |
| yarn install | 64 | 80+ npm packages from registry |
| Playwright | 34, 105 | Downloads Chromium binary (~100MB) |

### 11. Docker Compose pull policies

- `docker-compose.yaml:47` -- `pull_policy: always` (forces registry pull)
- `docker-compose.dev.yaml:47` -- `pull_policy: always`

### 12. Caddy automatic HTTPS / ACME

- `Caddyfile:14` -- Caddy auto-provisions TLS via Let's Encrypt. Needs `tls internal` or manual certs.

### 13. Kubernetes

- `k8s/chart/templates/deployment.yml:25` -- `imagePullPolicy: Always`
- `k8s/chart/Chart.yaml` -- Helm dependency on `https://charts.bitnami.com/bitnami` for PostgreSQL
- `k8s/chart/templates/ingress.yml` -- cert-manager annotation expects ACME issuer

---

## Summary

| Category | Severity | Impact | Count |
|----------|----------|--------|-------|
| CDN JS libraries | CRITICAL | Artifacts/charts blank | 5 libs, 7 files |
| Heroicons/UI icons | CRITICAL | Icons missing everywhere | 849 refs, 127 files |
| LLM APIs | CRITICAL | Core AI broken | 4 providers |
| OAuth/SSO | HIGH | External login broken | 3 providers |
| Intercom | HIGH | Console errors | 4 files |
| PostHog telemetry | HIGH | Failed requests (default ON) | 22 files |
| Slack/Teams | HIGH | Integrations broken | 2 adapters |
| Git operations | HIGH | Sync/PR broken | 1 service |
| Email/SMTP | HIGH | Reset/verify broken | external SMTP default |
| Cloud data sources | MEDIUM | Connectors need internet | 12 clients |
| External links | LOW | Dead nav links | 5 URLs |
| Docker build | BUILD | Can't build offline | 6+ fetches |
| Caddy TLS | INFRA | Cert provisioning fails | 1 config |
| K8s/Compose | INFRA | Image pulls fail | 3 configs |
