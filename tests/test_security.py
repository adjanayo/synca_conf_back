import pytest

from app.core.security import (
    WeakPasswordError,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_hash_and_verify_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed) is True


def test_verify_wrong_password_fails():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("wrong password", hashed) is False


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",  # too short
        "nouppercasehere1!",  # no uppercase
        "NOLOWERCASEHERE1!",  # no lowercase
        "NoDigitsHereEither!",  # no digit
        "NoSymbolsHere1234",  # no symbol
    ],
)
def test_validate_password_strength_rejects_weak_passwords(password):
    with pytest.raises(WeakPasswordError):
        validate_password_strength(password)


def test_validate_password_strength_accepts_strong_password():
    validate_password_strength("Correct-Horse-Battery-9")
