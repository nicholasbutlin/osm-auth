import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TokenStore(ABC):
    """Abstract base class for token storage backends."""

    @abstractmethod
    def save_token(
        self, token_data: Dict[str, Any] | Any
    ) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def get_token(self) -> Optional[Dict[str, Any]]:  # pragma: no cover - interface
        pass

    @abstractmethod
    def delete_token(self) -> None:  # pragma: no cover - interface
        pass


class InMemoryTokenStore(TokenStore):
    """In-memory token store for testing or ephemeral use."""

    def __init__(self, token: Dict[str, Any] | None = None) -> None:
        self._token = token
        self.saved: list[Dict[str, Any]] = []

    def save_token(self, token_data: Dict[str, Any] | Any) -> None:
        self._token = token_data  # type: ignore[assignment]
        try:
            # Maintain a history useful in tests; noop if token_data isn't dict-like
            if isinstance(token_data, dict):
                self.saved.append(token_data)
        except Exception:
            # Never raise in a test stub due to logging
            pass

    def get_token(self) -> Optional[Dict[str, Any]]:
        return self._token

    def delete_token(self) -> None:
        self._token = None


class JsonTokenStore(TokenStore):
    """File-based token store using JSON serialization."""

    def __init__(self, token_file_path: Path | str):
        self.token_file_path = Path(token_file_path)

    def save_token(self, token_data: Dict[str, Any] | Any) -> None:
        """Saves the token data to the JSON file."""
        try:
            with open(self.token_file_path, "w") as f:
                json.dump(token_data, f, indent=4)
            logger.debug(f"Token saved to {self.token_file_path}")
        except IOError as e:
            logger.error(f"Error saving token to {self.token_file_path}: {e}")

    def get_token(self) -> Optional[Dict[str, Any]]:
        """Retrieves the token data from the JSON file."""
        if not self.token_file_path.exists():
            logger.debug(f"Token file {self.token_file_path} not found.")
            return None
        try:
            with open(self.token_file_path, "r") as f:
                token_data = json.load(f)
            logger.debug(f"Token loaded from {self.token_file_path}")
            return token_data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading token from {self.token_file_path}: {e}")
            # Optionally, delete corrupted token file
            # self.token_file_path.unlink(missing_ok=True)
            return None

    def delete_token(self) -> None:
        """Deletes the token file."""
        try:
            self.token_file_path.unlink(missing_ok=True)
            logger.debug(f"Token file {self.token_file_path} deleted.")
        except IOError as e:
            logger.error(f"Error deleting token file {self.token_file_path}: {e}")
