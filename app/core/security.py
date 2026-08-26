import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()

# Password policy (security-hardening SKILL.md): min 12 chars, mixed case +
# digit + symbol, no forced periodic rotation. Enforced at account creation
# and password reset (Phase 6), not on every login -- an existing hash that
# predates a policy tightening must still verify.
PASSWORD_MIN_LENGTH = 12
_SYMBOL_PATTERN = re.compile(r"[^a-zA-Z0-9]")


class WeakPasswordError(ValueError):
    pass


def validate_password_strength(password: str) -> None:
    problems = []
    if len(password) < PASSWORD_MIN_LENGTH:
        problems.append(f"au moins {PASSWORD_MIN_LENGTH} caractères")
    if not any(c.islower() for c in password):
        problems.append("une minuscule")
    if not any(c.isupper() for c in password):
        problems.append("une majuscule")
    if not any(c.isdigit() for c in password):
        problems.append("un chiffre")
    if not _SYMBOL_PATTERN.search(password):
        problems.append("un symbole")

    if problems:
        raise WeakPasswordError("Le mot de passe doit contenir " + ", ".join(problems) + ".")


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, plain_password)
    except VerifyMismatchError:
        return False
