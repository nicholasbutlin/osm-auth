import time

import pytest

from auth.osm import OSMAuthConfig, OSMClient
from auth.token_store import InMemoryTokenStore


@pytest.fixture()
def env_osm(monkeypatch):
    monkeypatch.setenv("OSM_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("OSM_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("OSM_REDIRECT_URI", "http://localhost:8000/osm/callback")
    monkeypatch.setenv("OSM_SCOPES", "section:finance:read")
    monkeypatch.setenv("BASE_URL", "https://example.osm.local")
    monkeypatch.setenv("OSM_BANK_ACCOUNT_ID", "12345")


def test_config_builds_urls(env_osm):
    cfg = OSMAuthConfig()  # type: ignore[call-arg]
    assert cfg.token_url == "https://example.osm.local/oauth/token"
    assert cfg.authorize_url == "https://example.osm.local/oauth/authorize"


def test_interactive_authorize_opens_browser_waits_and_saves_token(
    monkeypatch, env_osm
):
    store = InMemoryTokenStore()
    client = OSMClient(token_store=store)

    # Stub out the authorization URL so it's deterministic
    monkeypatch.setattr(
        client, "authorization_url", lambda: "https://auth.local/authorize"
    )

    # Capture browser open
    opened = {}

    def fake_open(url):
        opened["url"] = url
        return True

    monkeypatch.setattr("webbrowser.open", fake_open)

    # Capture wait_for_oauth_callback call and return a fake callback URL
    calls = {}

    def fake_wait(redirect_uri, timeout_seconds=None, certfile=None, keyfile=None):
        calls["redirect_uri"] = redirect_uri
        calls["timeout_seconds"] = timeout_seconds
        return f"{redirect_uri}?code=abc123&state=xyz"

    monkeypatch.setattr("auth.osm.client.wait_for_oauth_callback", fake_wait)

    # Make the token exchange return a fixed token
    returned_token = {
        "access_token": "tok_123",
        "refresh_token": "ref_456",
        "token_type": "Bearer",
        "expires_at": time.time() + 3600,
    }

    def fake_fetch_token(**kwargs):
        # Simulate provider exchange. The client reads this into self.token in authlib.
        return dict(returned_token)

    monkeypatch.setattr(client, "fetch_token", fake_fetch_token)

    token = client.interactive_authorize(timeout_seconds=5)

    # Opened the browser to the expected URL
    assert opened.get("url") == "https://auth.local/authorize"

    # Waited on the configured redirect URI and honoured timeout
    assert calls.get("redirect_uri") == OSMAuthConfig().OSM_REDIRECT_URI  # type: ignore[call-arg] # noqa: E501
    assert calls.get("timeout_seconds") == 5

    # Exchanged and saved the token
    assert token == returned_token
    assert store.get_token() == returned_token


def test_get_or_refresh_token_reuses_valid_store_token(monkeypatch, env_osm):
    valid_token = {"access_token": "tok", "expires_at": time.time() + 3600}
    store = InMemoryTokenStore(valid_token)
    client = OSMClient(token_store=store)

    # If refresh is accidentally called, fail fast
    def fail_refresh(*args, **kwargs):
        raise AssertionError("refresh_token should not be called for valid token")

    monkeypatch.setattr(client, "refresh_token", fail_refresh)

    token = client.get_or_refresh_token()
    assert token == valid_token


def test_get_or_refresh_token_refreshes_and_persists_when_expired(monkeypatch, env_osm):
    now = int(time.time())
    expired_token = {
        "access_token": "old",
        "refresh_token": "ref",
        "expires_at": now - 10,
    }
    store = InMemoryTokenStore(expired_token)
    client = OSMClient(token_store=store)

    new_token = {
        "access_token": "new",
        "refresh_token": "ref",
        "expires_at": now + 7200,
    }

    def fake_refresh(token_url, refresh_token):
        # Simulate authlib refresh updating client.token
        client.token = dict(new_token)  # type: ignore[attr-defined]
        return dict(new_token)

    monkeypatch.setattr(client, "refresh_token", fake_refresh)

    token = client.get_or_refresh_token()
    assert token == new_token
    assert store.get_token() == new_token


def test_get_or_refresh_token_returns_none_without_any_token(env_osm):
    store = InMemoryTokenStore()
    client = OSMClient(token_store=store)

    assert client.get_or_refresh_token() is None


def test_get_token_falls_back_to_interactive_when_needed(monkeypatch, env_osm):
    # Start with no stored token; get_token should call interactive_authorize
    store = InMemoryTokenStore()
    client = OSMClient(token_store=store)

    called = {}
    interactive_token = {"access_token": "tokX", "expires_at": time.time() + 100}

    def fake_interactive(**kwargs):
        called["interactive"] = True
        return dict(interactive_token)

    monkeypatch.setattr(client, "interactive_authorize", fake_interactive)

    token = client.get_token(timeout_seconds=7)
    assert called.get("interactive") is True
    assert token == interactive_token
