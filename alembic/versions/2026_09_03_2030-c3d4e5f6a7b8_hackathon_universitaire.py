"""hackathon_universitaire

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-03 20:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: str | Sequence[str] | None = 'b2c3d4e5f6a7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_PERMISSION_CODES = ['hackathon.manage']

OLD_CAMPAIGN_WINDOW_KEYS = (
    'call_for_speaker', 'ticketing', 'call_for_partner',
    'call_for_ambassador', 'call_for_exhibitor', 'event',
)
NEW_CAMPAIGN_WINDOW_KEYS = OLD_CAMPAIGN_WINDOW_KEYS + (
    'hackathon_universitaire', 'call_for_community_certified',
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'hackathon_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('university_name', sa.String(length=200), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('project_name', sa.String(length=200), nullable=False),
        sa.Column('project_description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_hackathon_teams_university_name', 'hackathon_teams', ['university_name']
    )

    op.create_table(
        'hackathon_team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('study_level', sa.String(length=100), nullable=False),
        sa.Column('specialty', sa.String(length=150), nullable=False),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['hackathon_teams.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_hackathon_team_members_team_id', 'hackathon_team_members', ['team_id']
    )

    # Nouvelles clés de fenêtre de campagne : candidature Synca Community
    # Certified (deadline connue, cf. data/faq.ts front) et hackathon
    # universitaire (dates placeholder, à ajuster par le back-office comme
    # les autres fenêtres à leur création -- cf. 2c2d07493eb5).
    op.alter_column(
        'campaign_windows',
        'key',
        existing_type=sa.Enum(*OLD_CAMPAIGN_WINDOW_KEYS, name='campaign_window_key'),
        type_=sa.Enum(*NEW_CAMPAIGN_WINDOW_KEYS, name='campaign_window_key'),
        existing_nullable=False,
    )

    campaign_windows_table = sa.table(
        'campaign_windows',
        sa.column('key', sa.String),
        sa.column('start_at', sa.DateTime),
        sa.column('end_at', sa.DateTime),
    )
    op.bulk_insert(
        campaign_windows_table,
        [
            {
                'key': 'call_for_community_certified',
                'start_at': '2026-10-01 00:00:00',
                'end_at': '2026-12-31 23:59:59',
            },
            {
                'key': 'hackathon_universitaire',
                'start_at': '2026-10-01 00:00:00',
                'end_at': '2027-03-01 23:59:59',
            },
        ],
    )

    # Nouvelle permission admin.
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

    op.execute(
        "DELETE FROM campaign_windows WHERE `key` IN "
        "('hackathon_universitaire', 'call_for_community_certified')"
    )
    op.alter_column(
        'campaign_windows',
        'key',
        existing_type=sa.Enum(*NEW_CAMPAIGN_WINDOW_KEYS, name='campaign_window_key'),
        type_=sa.Enum(*OLD_CAMPAIGN_WINDOW_KEYS, name='campaign_window_key'),
        existing_nullable=False,
    )

    op.drop_index('ix_hackathon_team_members_team_id', table_name='hackathon_team_members')
    op.drop_table('hackathon_team_members')
    op.drop_index('ix_hackathon_teams_university_name', table_name='hackathon_teams')
    op.drop_table('hackathon_teams')
