from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import get_settings
from app.services.auth_service import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_access_token_round_trip():
    token = create_access_token(subject="42")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == "42"


def test_refresh_token_round_trip():
    token = create_refresh_token(subject="42")
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == "42"


def test_wrong_token_type_rejected():
    token = create_access_token(subject="42")
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="refresh")


def test_expired_token_rejected():
    settings = get_settings()
    now = datetime.now(UTC)
    expired_payload = {
        "sub": "42",
        "type": "access",
        "iat": now - timedelta(minutes=20),
        "exp": now - timedelta(minutes=5),
    }
    token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type="access")


def test_invalid_signature_rejected():
    token = create_access_token(subject="42")
    header, payload, signature = token.split(".")
    # Flip the middle character of the signature -- unlike the trailing
    # character, this always changes the decoded signature bytes (a
    # base64url tail character can map padding bits that don't survive
    # decoding, which made this test flaky when it tampered the last char).
    mid = len(signature) // 2
    flipped = "A" if signature[mid] != "A" else "B"
    tampered_signature = signature[:mid] + flipped + signature[mid + 1 :]
    tampered = f"{header}.{payload}.{tampered_signature}"

    with pytest.raises(InvalidTokenError):
        decode_token(tampered, expected_type="access")
