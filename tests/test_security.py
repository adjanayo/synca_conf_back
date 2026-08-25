from app.core.security import hash_password, verify_password


def test_hash_and_verify_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed) is True


def test_verify_wrong_password_fails():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("wrong password", hashed) is False
