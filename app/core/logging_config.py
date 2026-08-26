import sys
from pathlib import Path

from loguru import logger

from app.core.config import get_settings

# ROADMAP 8.1: 3 separate channels, each its own rotating file --
# security (90j) and payment (365j) get long retention for audit/compliance
# purposes; app is the default/unbound channel with a shorter housekeeping
# retention since it's debug noise, not a record of anything.
_SECURITY_RETENTION = "90 days"
_PAYMENT_RETENTION = "365 days"
_APP_RETENTION = "30 days"


def _is_channel(name: str):
    return lambda record: record["extra"].get("channel") == name


def _is_unbound_channel(record: dict) -> bool:
    return "channel" not in record["extra"]


def configure_logging() -> None:
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(sys.stderr, level="INFO", filter=_is_unbound_channel)

    logger.add(
        log_dir / "app.log",
        level="INFO",
        rotation="00:00",
        retention=_APP_RETENTION,
        filter=_is_unbound_channel,
    )
    logger.add(
        log_dir / "security.log",
        level="INFO",
        rotation="00:00",
        retention=_SECURITY_RETENTION,
        filter=_is_channel("security"),
    )
    logger.add(
        log_dir / "payment.log",
        level="INFO",
        rotation="00:00",
        retention=_PAYMENT_RETENTION,
        filter=_is_channel("payment"),
    )
