import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DIR = Path(__file__).resolve(strict=True).parent
ROOT_DIR = DIR.parent

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

AUTH_CACHE_DIR = DATA_DIR / "auth_cache"
AUTH_CACHE_DIR.mkdir(exist_ok=True)
