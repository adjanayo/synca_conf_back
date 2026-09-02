import asyncio
import sys

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.security import (
    WeakPasswordError,
    hash_password,
    validate_password_strength,
)
from app.models import AdminUser, Role


async def main() -> None:
    settings = get_settings()
    email = settings.admin_email
    password = settings.admin_password
    if not email or not password:
        print(
            "Erreur : ADMIN_EMAIL et ADMIN_PASSWORD doivent être définis "
            "(via .env ou l'environnement).",
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        validate_password_strength(password)
    except WeakPasswordError as exc:
        print(f"Erreur : ADMIN_PASSWORD invalide — {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    async with AsyncSessionLocal() as db:
        role = (
            await db.execute(select(Role).where(Role.name == "superadmin"))
        ).scalar_one()
        db.add(
            AdminUser(
                email=email,
                password_hash=hash_password(password),
                role_id=role.id,
            )
        )
        await db.commit()
        print(f"Compte créé : {email}")


if __name__ == "__main__":
    asyncio.run(main())
