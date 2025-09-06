from __future__ import annotations

import ssl
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


def wait_for_oauth_callback(
    redirect_uri: str,
    timeout_seconds: Optional[int] = 180,
    *,
    certfile: Optional[str | Path] = None,
    keyfile: Optional[str | Path] = None,
) -> str:
    """Start a tiny local HTTP server and wait for a single OAuth callback.

    Args:
        redirect_uri: The redirect URI to listen on (e.g.
            http://127.0.0.1:8765/osm/callback)
        timeout_seconds: Optional timeout; None means wait indefinitely.

    Returns:
        The full callback URL (including query string) provider redirected to.
    """
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    expected_path = parsed.path or "/"

    result: dict[str, str] = {}
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (FastAPI style not enforced here)
            if self.path.startswith(expected_path):
                result["url"] = f"{parsed.scheme}://{host}:{port}{self.path}"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h3>Authentication complete.</h3>"
                    b"<p>You may close this window.</p></body></html>"
                )
                done.set()
            else:
                # Not our path; return 404 to be explicit
                self.send_error(404)

        # Silence default logging
        def log_message(self, format: str, *args):  # noqa: A003
            return

    httpd = HTTPServer((host, port), Handler)
    httpd.timeout = 0.5  # type: ignore[attr-defined]

    # If HTTPS is requested, wrap the server socket with TLS
    if parsed.scheme == "https":
        # Default to repository local dev certs if not provided
        if certfile is None or keyfile is None:
            # Project root is two levels up from this file's directory:
            # this file -> src/auth/callback_server.py
            # parents[2] -> repo root
            repo_root = Path(__file__).resolve().parents[2]
            default_cert = repo_root / "certs" / "localhost.pem"
            default_key = repo_root / "certs" / "localhost-key.pem"
            certfile = certfile or default_cert
            keyfile = keyfile or default_key

        # Validate existence and provide a clear error if missing
        if not Path(certfile).exists() or not Path(keyfile).exists():
            raise FileNotFoundError(
                "HTTPS redirect requested but cert or key not found. "
                f"Tried certfile={certfile} keyfile={keyfile}. "
                "Generate dev certs with mkcert (see certs/readme.md) or pass "
                "explicit paths."
            )

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(certfile), keyfile=str(keyfile))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    try:

        def serve():
            while not done.is_set():
                httpd.handle_request()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()

        # Wait for completion or timeout
        if not done.wait(timeout=timeout_seconds):
            raise TimeoutError("Timed out waiting for OAuth callback")

        return result["url"]
    finally:
        try:
            httpd.server_close()
        except Exception:
            pass
