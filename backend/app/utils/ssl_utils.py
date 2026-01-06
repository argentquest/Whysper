import logging
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import Settings

logger = logging.getLogger(__name__)


def _normalize_path(path_value: Optional[str], base_dir: Path) -> Optional[Path]:
    """Resolve cert/key paths relative to the backend directory."""
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def build_ssl_kwargs(settings: Settings) -> Dict[str, Any]:
    """
    Build uvicorn SSL keyword arguments based on settings.

    Uses provided SSL certificate and key files.
    """
    if not settings.ssl_enabled:
        return {}

    backend_dir = Path(__file__).resolve().parents[2]

    cert_path = _normalize_path(settings.ssl_certfile, backend_dir)
    key_path = _normalize_path(settings.ssl_keyfile, backend_dir)

    if not cert_path or not key_path:
        raise RuntimeError("SSL_ENABLED is true but SSL_CERTFILE or SSL_KEYFILE is missing")

    ssl_kwargs: Dict[str, Any] = {
        "ssl_certfile": str(cert_path),
        "ssl_keyfile": str(key_path),
    }

    if settings.ssl_keyfile_password:
        ssl_kwargs["ssl_keyfile_pwd"] = settings.ssl_keyfile_password

    return ssl_kwargs
