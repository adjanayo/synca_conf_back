"""encrypt users phone_whatsapp and special_needs (PII 7.8)

Revision ID: d7d5f8910852
Revises: e3a07849ada9
Create Date: 2026-08-26 14:44:44.458071

"""
from typing import Sequence, Union

import sqlalchemy as sa
from cryptography.fernet import Fernet

from alembic import op
from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision: str = 'd7d5f8910852'
down_revision: Union[str, Sequence[str], None] = 'e3a07849ada9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


users_table = sa.table(
    'users',
    sa.column('id', sa.Integer),
    sa.column('phone_whatsapp', sa.Text),
    sa.column('special_needs', sa.Text),
)


def upgrade() -> None:
    # phone_whatsapp was VARCHAR(20) -- nowhere near enough room for a
    # Fernet token (base64 of IV + ciphertext + HMAC, well over 100 bytes
    # even for a short phone number). special_needs is already TEXT, so no
    # DDL change needed there, only the data rewrite below.
    op.alter_column(
        'users', 'phone_whatsapp', existing_type=sa.String(length=20), type_=sa.Text(),
        existing_nullable=False,
    )

    fernet = Fernet(get_settings().fernet_key.encode())
    connection = op.get_bind()
    rows = connection.execute(
        sa.select(users_table.c.id, users_table.c.phone_whatsapp, users_table.c.special_needs)
    ).fetchall()

    for row in rows:
        connection.execute(
            users_table.update()
            .where(users_table.c.id == row.id)
            .values(
                phone_whatsapp=fernet.encrypt(row.phone_whatsapp.encode()).decode(),
                special_needs=(
                    fernet.encrypt(row.special_needs.encode()).decode()
                    if row.special_needs is not None
                    else None
                ),
            )
        )


def downgrade() -> None:
    fernet = Fernet(get_settings().fernet_key.encode())
    connection = op.get_bind()
    rows = connection.execute(
        sa.select(users_table.c.id, users_table.c.phone_whatsapp, users_table.c.special_needs)
    ).fetchall()

    for row in rows:
        connection.execute(
            users_table.update()
            .where(users_table.c.id == row.id)
            .values(
                phone_whatsapp=fernet.decrypt(row.phone_whatsapp.encode()).decode(),
                special_needs=(
                    fernet.decrypt(row.special_needs.encode()).decode()
                    if row.special_needs is not None
                    else None
                ),
            )
        )

    op.alter_column(
        'users', 'phone_whatsapp', existing_type=sa.Text(), type_=sa.String(length=20),
        existing_nullable=False,
    )
