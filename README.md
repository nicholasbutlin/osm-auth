# OSM Auth Module

Reusable OAuth 2.0 helper for Online Scout Manager (OSM). It wraps an `authlib` `OAuth2Client` and provides simple methods to start the Authorization Code flow and exchange a callback URL for tokens. Use it from web apps (FastAPI), CLI tools, or scripts.

Quick highlights:
- `get_token(...)`: Reuse/refresh a stored token or run an interactive browser login and persist the result.
- Web apps use `authorization_url()` and `fetch_token_from_callback(...)`; no local callback server needed.

## Configuration

Set environment variables (e.g., via `.env`) recognised by `OSMAuthConfig`:

- `OSM_CLIENT_ID`: Your OSM OAuth client ID
- `OSM_CLIENT_SECRET`: Your OSM OAuth client secret
- `OSM_REDIRECT_URI`: Redirect URI registered with OSM
- `OSM_SCOPES` (optional): Defaults to `section:finance:read`
- `BASE_URL` (optional): Defaults to `https://www.onlinescoutmanager.co.uk`
- `OSM_BANK_ACCOUNT_ID` (optional): Kept for compatibility with the transactions integration

Example `.env` snippet:

```text
OSM_CLIENT_ID=xxxx
OSM_CLIENT_SECRET=yyyy
OSM_REDIRECT_URI=https://localhost:8765/osm/callback
OSM_SCOPES=section:finance:read
```

## CLI/Desktop (Built‑in Callback Waiter)

```python
from auth.osm import OSMClient

client = OSMClient()
# Reuse/refresh if possible; otherwise open the browser and wait locally
token = client.get_token(timeout_seconds=180)
print("Access token acquired.")
```

## Web (FastAPI) Pattern (Deprecated in this repo)

The project is now CLI-only. The following example remains for reference if you adapt the auth client in a web app.

```python
from fastapi import APIRouter, Request
from auth.osm import OSMClient

router = APIRouter()
client = OSMClient()

@router.get("/osm/login")
def login():
    return {"authorize_url": client.authorization_url()}

@router.get("/osm/callback")
def callback(request: Request):
    token = client.fetch_token_from_callback(str(request.url))
    # Persist token if desired, then proceed
    # Can call any OSM API with client here, or reuse client in other routes
    return {"ok": True}
```

## Persistence and Headless/CI

OSM requires an interactive consent at least once. Tokens are persisted by default to `data/auth_cache/osm_token.json`.

- First run (interactive, local):
  - CLI: `auth.get_token()` opens a browser, waits for the redirect, exchanges and saves the token.
  - Web: call `fetch_token_from_callback(...)` in your callback handler; it is saved automatically.

- Later (headless/CI):
  - Use `get_or_refresh_token()` to reuse or refresh without opening a browser:

```python
from auth.osm import OSMClient
from auth.token_store import JsonTokenStore

# Optionally choose a custom token path (seed this once via interactive login)
store = JsonTokenStore("/secure/path/osm_token.json")

client = OSMClient(token_store=store)
token = client.get_or_refresh_token()
if not token:
    raise RuntimeError(
        "No valid token available; perform one interactive login to seed the token store."
    )
```

## OSM Reference Notes

- For pure server-to-server automation, OSM does not provide service accounts; an initial interactive login is required.
- Need to make sure scopes match your app's registered scopes.

See `docs/osm_oauth_reference.md` for the full OSM OAuth 2.0 reference (endpoints, scopes, and guidance).

## Local HTTPS Certificates

If your `OSM_REDIRECT_URI` uses `https` (e.g. `https://localhost:8765/osm/callback`), the embedded callback server requires local TLS certificates.
By default the code looks for `certs/localhost.pem` and `certs/localhost-key.pem` at the repo root.

See `docs/local_certs.md` for instructions to generate dev certificates with mkcert and place them in the `certs/` directory.
