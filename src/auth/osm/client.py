import logging
import time
import webbrowser

from authlib.integrations.httpx_client import OAuth2Client

from auth.callback_server import wait_for_oauth_callback
from auth.osm.config import OSMAuthConfig
from auth.token_store import JsonTokenStore, TokenStore
from data_store import AUTH_CACHE_DIR

logger = logging.getLogger(__name__)

OSM_TOKEN_PATH = AUTH_CACHE_DIR / "osm_token.json"


class OSMClient(OAuth2Client):
    """Reusable OSM Client and helper wrapping an OAuth2Client.

    Provides an initialized `OAuth2Client`, an authorization URL generator,
    and a helper to exchange the callback URL for tokens.
    """

    def __init__(
        self,
        config: OSMAuthConfig | None = None,
        token_store: TokenStore | None = None,
    ) -> None:
        self.cfg = config or OSMAuthConfig()  # type: ignore[call-arg]

        if token_store is not None:
            self.token_store = token_store
        else:
            self.token_store = JsonTokenStore(OSM_TOKEN_PATH)

        super().__init__(
            client_id=self.cfg.OSM_CLIENT_ID,
            client_secret=self.cfg.OSM_CLIENT_SECRET,
            redirect_uri=self.cfg.OSM_REDIRECT_URI,
            scope=self.cfg.OSM_SCOPES,
            token_endpoint=self.cfg.token_url,
        )

    def authorization_url(self) -> str:
        url, _ = self.create_authorization_url(self.cfg.authorize_url)
        return url

    def fetch_token_from_callback(self, callback_url: str) -> dict:
        """Exchange the OAuth2 authorization response URL for tokens.

        Returns the token dictionary as provided by the provider.
        """
        token = self.fetch_token(authorization_response=str(callback_url))
        self.token_store.save_token(token)
        return token

    def interactive_authorize(
        self,
        *,
        timeout_seconds: int | None = 180,
        certfile: str | None = None,
        keyfile: str | None = None,
    ) -> dict:
        """Open browser, wait for callback, exchange for tokens."""
        webbrowser.open(self.authorization_url())

        callback_url = wait_for_oauth_callback(
            self.cfg.OSM_REDIRECT_URI,
            timeout_seconds,
            certfile=certfile,
            keyfile=keyfile,
        )

        return self.fetch_token_from_callback(callback_url)

    def _token_is_valid(self, skew_seconds: int = 30) -> bool:
        """Best-effort check for token validity based on expires_at.

        If no expiry info is found, assume valid.
        """
        if not self.token:
            return False

        expires_at = self.token.get("expires_at", False)  # seconds since epoch
        if isinstance(expires_at, (int, float)):
            return (time.time() + skew_seconds) < float(expires_at)

        return False

    def get_or_refresh_token(self) -> dict | None:
        """Return an existing valid token, or refresh it if possible.

        Does not open a browser or wait for callbacks. Returns None if no
        valid/refreshable token is available.
        """
        # Prefer token currently on the client
        token = getattr(self, "token", None)
        if not token and self.token_store:
            token = self.token_store.get_token()
            if token:
                self.token = token  # type: ignore[attr-defined]

        if self._token_is_valid():
            return self.token

        # Attempt refresh if possible
        if self.token and self.token.get("refresh_token"):
            try:
                self.refresh_token(
                    self.cfg.token_url, refresh_token=self.token["refresh_token"]
                )
                self.token_store.save_token(self.token)

            except Exception as e:
                logger.info(f"Token refresh failed: {e}")
                return None

            return self.token

        return None

    def get_token(
        self,
        *,
        timeout_seconds: int | None = 180,
        certfile: str | None = None,
        keyfile: str | None = None,
    ) -> dict:
        """Return a usable token; refresh or interact as needed.

        - Reuses an existing valid token if present.
        - Refreshes via refresh_token if expired and refreshable.
        - Otherwise, runs the interactive flow, which opens a browser,
          waits for the callback, exchanges for tokens, and persists them.

        Args:
            timeout_seconds: How long to wait for the callback in the
                interactive flow. Ignored if not running the interactive flow.
            certfile: Optional TLS cert file for the callback server.
            keyfile: Optional TLS key file for the callback server.

        Returns:
            The token dictionary as provided by the provider.
        """
        token = self.get_or_refresh_token()
        if token:
            return token

        return self.interactive_authorize(
            timeout_seconds=timeout_seconds,
            certfile=certfile,
            keyfile=keyfile,
        )
