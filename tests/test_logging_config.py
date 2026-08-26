from pathlib import Path

from loguru import logger

from app.core.logging_config import configure_logging


def test_configure_logging_routes_channels_to_separate_files(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    try:
        configure_logging()
        logger.bind(channel="security").warning("security-event")
        logger.bind(channel="payment").info("payment-event")
        logger.info("app-event")
    finally:
        get_settings.cache_clear()
        configure_logging()

    security_log = Path(tmp_path, "security.log").read_text()
    payment_log = Path(tmp_path, "payment.log").read_text()
    app_log = Path(tmp_path, "app.log").read_text()

    assert "security-event" in security_log
    assert "payment-event" not in security_log

    assert "payment-event" in payment_log
    assert "security-event" not in payment_log

    assert "app-event" in app_log
    assert "security-event" not in app_log
    assert "payment-event" not in app_log
