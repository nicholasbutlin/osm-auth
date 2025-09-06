import socket
from pathlib import Path
import time

import httpx
import pytest

from auth.callback_server import wait_for_oauth_callback


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_wait_for_oauth_callback_http_returns_full_url():
    port = _free_port()
    redirect = f"http://127.0.0.1:{port}/osm/callback"

    url_holder = {}

    def run_server():
        url_holder["url"] = wait_for_oauth_callback(redirect, timeout_seconds=5)

    import threading

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # Trigger the callback
    resp = httpx.get(f"{redirect}?code=abc&state=xyz", timeout=5)
    assert resp.status_code == 200

    t.join(timeout=5)
    assert "url" in url_holder
    assert url_holder["url"].startswith(f"http://127.0.0.1:{port}/osm/callback?code=")


@pytest.mark.skipif(
    not (
        Path("certs/localhost.pem").exists()
        and Path("certs/localhost-key.pem").exists()
    ),
    reason="Dev HTTPS certs not present",
)
def test_wait_for_oauth_callback_https_works_with_dev_certs():
    port = _free_port()
    # Use 127.0.0.1 to avoid potential IPv6 localhost resolution causing timeouts
    redirect = f"https://127.0.0.1:{port}/osm/callback"

    url_holder = {}

    def run_server():
        url_holder["url"] = wait_for_oauth_callback(redirect, timeout_seconds=10)

    import threading

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    # Give the server a short moment to start
    time.sleep(0.1)

    # Trigger the callback (skip cert verification for local dev certs)
    resp = httpx.get(f"{redirect}?code=abc&state=xyz", timeout=10, verify=False)
    assert resp.status_code == 200

    t.join(timeout=5)
    assert "url" in url_holder
    assert url_holder["url"].startswith(
        f"https://127.0.0.1:{port}/osm/callback?code="
    ) or url_holder["url"].startswith(f"https://localhost:{port}/osm/callback?code=")
