"""event_settings, pass_types & sessions admin permissions

Revision ID: 547ad7a3ad02
Revises: b1c2d3e4f5a6
Create Date: 2026-09-02 16:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '547ad7a3ad02'
down_revision: str | Sequence[str] | None = 'b1c2d3e4f5a6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_PERMISSION_CODES = [
    'pass_types.manage',
    'event_settings.manage',
    'sessions.manage',
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'event_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('venue', sa.String(length=200), nullable=False),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Seed : ligne singleton (id=1), valeurs actuelles en dur côté front
    # (src/data/parameter.ts), reprises ici comme valeurs par défaut modifiables.
    event_settings_table = sa.table(
        'event_settings',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('venue', sa.String),
    )
    op.bulk_insert(
        event_settings_table,
        [
            {
                'id': 1,
                'name': 'Synca Cyber',
                'venue': 'Dakar, Sénégal',
            },
        ],
    )

    # Nouvelles permissions admin (Phase I : PassType, EventSettings, Programme).
    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    roles_table = sa.table('roles', sa.column('id', sa.Integer), sa.column('name', sa.String))
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )

    op.bulk_insert(permissions_table, [{'code': code} for code in NEW_PERMISSION_CODES])

    connection = op.get_bind()
    superadmin_id = connection.execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'superadmin')
    ).scalar_one()
    new_permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(NEW_PERMISSION_CODES)
        )
    ).scalars().all()
    op.bulk_insert(
        role_permissions_table,
        [
            {'role_id': superadmin_id, 'permission_id': pid}
            for pid in new_permission_ids
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(NEW_PERMISSION_CODES)
        )
    ).scalars().all()

    if permission_ids:
        connection.execute(
            sa.text(
                "DELETE FROM role_permissions WHERE permission_id IN :ids"
            ).bindparams(sa.bindparam('ids', expanding=True)),
            {'ids': permission_ids},
        )
        connection.execute(
            sa.text("DELETE FROM permissions WHERE id IN :ids").bindparams(
                sa.bindparam('ids', expanding=True)
            ),
            {'ids': permission_ids},
        )

    op.drop_table('event_settings')
