# Fix: Auto-persist encryption key across container restarts

## Problem

When someone forks MetricChat and runs via Docker without setting `MC_ENCRYPTION_KEY`, the app generates a random Fernet key in memory on each startup. After a container restart, a new key is generated and all stored credentials (LLM API keys, data source passwords, etc.) become undecryptable — `cryptography.fernet.InvalidToken` is raised with an empty message, causing 500 errors on any chat completion.

The `start.sh` script already warns about this but doesn't persist the key.

## Root Cause

- `backend/app/settings/app_config.py` defines `encryption_key` with `default_factory=generate_fernet_key` — a new random key every time
- `start.sh` generates a key if `MC_ENCRYPTION_KEY` is empty, but only stores it in the shell process environment
- Docker Compose passes `MC_ENCRYPTION_KEY=${MC_ENCRYPTION_KEY:-}` which resolves to empty string if not in `.env`
- 6 model files use `Fernet(settings.app_config.encryption_key)` to encrypt/decrypt credentials with no `InvalidToken` handling
- On restart: new key → old credentials undecryptable → empty error message → 500 Internal Server Error

## Fix

### 1. `start.sh` — Persist key to file (primary fix)

Change the key generation block (lines 7-13) to:
- Check if a persisted key file exists at `/app/backend/db/.encryption_key` and read it
- If no file and no env var: generate a key, write it to the file, and export it
- If env var is provided: use it (don't write to file — user manages their own key)

```bash
ENCRYPTION_KEY_FILE="/app/backend/db/.encryption_key"

if [ -z "$MC_ENCRYPTION_KEY" ]; then
    if [ -f "$ENCRYPTION_KEY_FILE" ]; then
        export MC_ENCRYPTION_KEY=$(cat "$ENCRYPTION_KEY_FILE")
        echo "🔑 Loaded encryption key from $ENCRYPTION_KEY_FILE"
    else
        export MC_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        echo "$MC_ENCRYPTION_KEY" > "$ENCRYPTION_KEY_FILE"
        chmod 600 "$ENCRYPTION_KEY_FILE"
        echo "🔑 Generated and saved encryption key to $ENCRYPTION_KEY_FILE"
    fi
fi
```

### 2. `docker-compose.yaml` — Add `app_data` volume

Add a named volume for `/app/backend/db` so the key file (and SQLite DB if used) persists across container restarts:

```yaml
# In the app service volumes section:
volumes:
  - ./metricchat.yaml:/app/metricchat.yaml:ro
  - app_data:/app/backend/db              # NEW: persists encryption key + SQLite DB
  - uploads_data:/app/backend/uploads
  - branding_data:/app/backend/branding_uploads
  - logs_data:/app/backend/logs

# In the top-level volumes section:
volumes:
  app_data:
    driver: local
  # ... existing volumes ...
```

### 3. `docker-compose.dev.yaml` — Same volume addition

Mirror the volume change for the dev compose file (using `app_data_dev` name).

### 4. Better error messages — 6 model files

Wrap `decrypt_credentials()` in all model files to catch `InvalidToken` and raise a descriptive error instead of an empty one:

```python
from cryptography.fernet import Fernet, InvalidToken

def decrypt_credentials(self) -> dict:
    fernet = Fernet(settings.app_config.encryption_key)
    try:
        # existing decrypt logic
        return json.loads(fernet.decrypt(self.api_key.encode()).decode()), ...
    except InvalidToken:
        raise ValueError(
            f"Failed to decrypt credentials for '{self.name}'. "
            "The encryption key may have changed since these credentials were saved. "
            "Please re-enter your API key in Settings > LLM."
        )
```

Files to update:
- `backend/app/models/llm_provider.py`
- `backend/app/models/connection.py`
- `backend/app/models/user_data_source_credentials.py`
- `backend/app/models/user_connection_credentials.py`
- `backend/app/models/external_platform.py`
- `backend/app/models/git_repository.py`

## Verification

1. `docker compose -f docker-compose.dev.yaml up -d` **without** `MC_ENCRYPTION_KEY` set
2. Add an LLM API key through the UI (Settings > LLM)
3. Send a chat message — should work
4. `docker compose -f docker-compose.dev.yaml restart app`
5. Send another chat message — should still work (key persisted)
6. Verify: `docker exec metricchat-app-dev cat /app/backend/db/.encryption_key` shows the saved key

## Files Modified

| File | Change |
|------|--------|
| `start.sh` | Auto-persist generated encryption key to file |
| `docker-compose.yaml` | Add `app_data` volume for `/app/backend/db` |
| `docker-compose.dev.yaml` | Add `app_data_dev` volume for `/app/backend/db` |
| `backend/app/models/llm_provider.py` | Catch `InvalidToken`, raise descriptive error |
| `backend/app/models/connection.py` | Catch `InvalidToken`, raise descriptive error |
| `backend/app/models/user_data_source_credentials.py` | Catch `InvalidToken`, raise descriptive error |
| `backend/app/models/user_connection_credentials.py` | Catch `InvalidToken`, raise descriptive error |
| `backend/app/models/external_platform.py` | Catch `InvalidToken`, raise descriptive error |
| `backend/app/models/git_repository.py` | Catch `InvalidToken`, raise descriptive error |
