# Changelog

All notable changes to MetricChat since forking from [Bag of Words](https://github.com/bagofwords1/bagofwords) are documented here.

## [Unreleased]

## 2026-02-26

### Added
- Encryption key persistence so `MC_ENCRYPTION_KEY` survives container restarts without logging users out
- Improved error handling for credential decryption failures

### Changed
- Button colors changed from blue to primary across bulk modals, instruction tables, and test components for brand consistency
- New MetricChat brand colors (teal palette), logo assets, and custom font families
- `brand.css` and updated `app.config.ts` with MetricChat identity

## 2026-02-25

### Added
- Plans for CSV upload feature to enable instant queryable data sources

### Changed
- **Full rebrand from Bag of Words to MetricChat**
  - All user-visible strings replaced (UI, docs, CLI output, error messages)
  - Env var prefix: `BOW_` → `MC_` (backward-compat fallbacks kept)
  - Config files: `bow-config.yaml` → `metricchat.yaml`
  - Python modules: `BowConfig` → `AppConfig`, `bow_config.py` → `app_config.py`, `bow_settings.py` → `app_settings.py`
  - DB JSON field: `bow_credit` → `show_credit` (legacy fallback kept)
  - License system: new RSA keypair, issuer `metricchat.io`, prefix `mc_lic_` (backward compat with `bow_lic_`)
  - Docker images: `metricchat/metricchat`
  - Helm chart: renamed to `metricchat`, service account `metricchatapp`
  - Git branch prefix: `BOW-` → `MC-`
  - Redshift session names: `metricchat_*`
  - EE license entity: Midwest Marketing Group LLC
- Disabled telemetry and Intercom by default in all config YAMLs
- Docker Compose image updated to `walrusquant/metricchat:latest`
- README rewritten as MetricChat product page with feature grid, integrations table, and quick start
- CLAUDE.md and DEV.md updated to reflect MetricChat
- Archived Bag of Words planning docs and changelog to `.bow-archive/`

### Fixed
- Restored `VERSION` file to project root (accidentally archived during rebrand)
- Added fallback guard for missing `VERSION` in `config.py`
- Changed `pytest.fail` to `pytest.skip` when `OPENAI_API_KEY_TEST` is missing
- Registered `unit` marker in conftest and added `@pytest.mark.unit` decorators
