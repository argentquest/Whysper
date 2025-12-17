import datetime
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

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


def _generate_self_signed_certificate(cert_path: Path, key_path: Path, hostnames: Iterable[str]) -> None:
    """Create a self-signed certificate for local HTTPS development."""
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "cryptography is required to generate self-signed certificates. "
            "Install it with `pip install cryptography` or provide SSL_CERTFILE/SSL_KEYFILE."
        ) from exc

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Whysper"),
            x509.NameAttribute(NameOID.COMMON_NAME, hostnames[0]),
        ]
    )

    alt_names = [x509.DNSName(host) for host in hostnames]
    now = datetime.datetime.utcnow()

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName(alt_names), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    with open(key_path, "wb") as key_file:
        key_file.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(cert_path, "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    logger.info(f"Generated self-signed certificate at {cert_path}")


def build_ssl_kwargs(settings: Settings) -> Dict[str, Any]:
    """
    Build uvicorn SSL keyword arguments based on settings.

    Supports automatic self-signed certificate generation when SSL_SELF_SIGNED is enabled.
    """
    if not settings.ssl_enabled:
        return {}

    backend_dir = Path(__file__).resolve().parents[2]

    cert_path = _normalize_path(settings.ssl_certfile, backend_dir)
    key_path = _normalize_path(settings.ssl_keyfile, backend_dir)

    if settings.ssl_self_signed:
        default_cert_dir = backend_dir / "certs"
        cert_path = cert_path or default_cert_dir / "selfsigned.crt"
        key_path = key_path or default_cert_dir / "selfsigned.key"
        _generate_self_signed_certificate(
            cert_path,
            key_path,
            hostnames=["localhost", "127.0.0.1"],
        )

    if not cert_path or not key_path:
        raise RuntimeError("SSL_ENABLED is true but SSL_CERTFILE or SSL_KEYFILE is missing")

    ssl_kwargs: Dict[str, Any] = {
        "ssl_certfile": str(cert_path),
        "ssl_keyfile": str(key_path),
    }

    if settings.ssl_keyfile_password:
        ssl_kwargs["ssl_keyfile_password"] = settings.ssl_keyfile_password

    return ssl_kwargs
