"""pass_contents and partner_levels admin

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-03 22:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: str | Sequence[str] | None = 'c3d4e5f6a7b8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_PERMISSION_CODES = ['partner_levels.manage']


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'pass_contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label'),
    )

    op.create_table(
        'pass_type_contents',
        sa.Column('pass_type_id', sa.Integer(), nullable=False),
        sa.Column('pass_content_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['pass_type_id'], ['pass_types.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pass_content_id'], ['pass_contents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('pass_type_id', 'pass_content_id'),
    )

    # `inclusions` (texte libre) remplacé par le catalogue `pass_contents` +
    # la table de liaison ci-dessus -- ROADMAP_PUBLIC_SEO.md Partie 8, choix
    # des contenus à la création d'un pass plutôt que texte retapé à chaque
    # fois. Aucun pass en base au moment de cette migration (perte de
    # données nulle en pratique) -- pas de script de conversion texte libre
    # -> lignes du catalogue, aurait été deviné sans valeur ajoutée.
    op.drop_column('pass_types', 'inclusions')

    # Nouvelle permission admin (CRUD paliers de partenariat, jusqu'ici
    # lecture publique seule, jamais éditable au dashboard).
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

    op.add_column('pass_types', sa.Column('inclusions', sa.Text(), nullable=True))
    op.drop_table('pass_type_contents')
    op.drop_table('pass_contents')
