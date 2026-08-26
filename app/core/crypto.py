from cryptography.fernet import Fernet
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.core.config import get_settings


class EncryptedString(TypeDecorator):
    """Application-layer encryption for genuinely sensitive PII (7.8).

    Not for fields used in WHERE-equality lookups or unique constraints --
    Fernet is non-deterministic (a fresh IV per encryption), so the same
    plaintext never produces the same ciphertext twice. Backed by Text since
    a Fernet token is meaningfully longer than its plaintext.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        fernet = Fernet(get_settings().fernet_key.encode())
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is None:
            return None
        fernet = Fernet(get_settings().fernet_key.encode())
        return fernet.decrypt(value.encode()).decode()
