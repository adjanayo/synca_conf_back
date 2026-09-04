"""revert_hackathon_participant_link

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-04 02:00:00.000000

Retour en arrière explicite demandé par l'utilisateur : "les membres de
l'équipe du hackathon ne seront pas pris dans les inscrits, on doit entrer
les données depuis le dashboard" -- annule f6a7b8c9d0e1 (lien
hackathon_team_members.user_id vers `users` + permission `participants.manage`
+ endpoints /api/admin/participants). Les deux populations (inscrits
billetterie / membres hackathon) restent volontairement disjointes.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a7b8c9d0e1f2'
down_revision: str | Sequence[str] | None = 'f6a7b8c9d0e1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

REMOVED_PERMISSION_CODES = ['participants.manage']


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(REMOVED_PERMISSION_CODES)
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

    op.drop_constraint(
        'fk_hackathon_team_members_user_id', 'hackathon_team_members', type_='foreignkey'
    )
    op.drop_index('ix_hackathon_team_members_user_id', table_name='hackathon_team_members')
    op.drop_column('hackathon_team_members', 'user_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'hackathon_team_members', sa.Column('user_id', sa.Integer(), nullable=True)
    )
    op.create_index(
        'ix_hackathon_team_members_user_id', 'hackathon_team_members', ['user_id']
    )
    op.create_foreign_key(
        'fk_hackathon_team_members_user_id',
        'hackathon_team_members',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL',
    )

    permissions_table = sa.table(
        'permissions', sa.column('id', sa.Integer), sa.column('code', sa.String)
    )
    roles_table = sa.table('roles', sa.column('id', sa.Integer), sa.column('name', sa.String))
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )

    op.bulk_insert(permissions_table, [{'code': code} for code in REMOVED_PERMISSION_CODES])

    connection = op.get_bind()
    superadmin_id = connection.execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == 'superadmin')
    ).scalar_one()
    new_permission_ids = connection.execute(
        sa.select(permissions_table.c.id).where(
            permissions_table.c.code.in_(REMOVED_PERMISSION_CODES)
        )
    ).scalars().all()
    op.bulk_insert(
        role_permissions_table,
        [
            {'role_id': superadmin_id, 'permission_id': pid}
            for pid in new_permission_ids
        ],
    )
