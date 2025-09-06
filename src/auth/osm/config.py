from pydantic_settings import BaseSettings


class OSMAuthConfig(BaseSettings):
    """Configuration for OSM OAuth and base URLs.

    Uses environment variables compatible with the existing integration:
    - OSM_CLIENT_ID
    - OSM_CLIENT_SECRET
    - OSM_REDIRECT_URI
    - OSM_SCOPES (default: "section:finance:read")
    - BASE_URL (default: "https://www.onlinescoutmanager.co.uk")
    - OSM_BANK_ACCOUNT_ID (kept here for backward-compatibility)
    """

    OSM_CLIENT_ID: str
    OSM_CLIENT_SECRET: str
    OSM_REDIRECT_URI: str
    OSM_SCOPES: str = "section:finance:read"
    BASE_URL: str = "https://www.onlinescoutmanager.co.uk"

    # Not strictly auth, but retained for compatibility with callers
    OSM_BANK_ACCOUNT_ID: str

    @property
    def token_url(self) -> str:
        return f"{self.BASE_URL}/oauth/token"

    @property
    def authorize_url(self) -> str:
        return f"{self.BASE_URL}/oauth/authorize"
