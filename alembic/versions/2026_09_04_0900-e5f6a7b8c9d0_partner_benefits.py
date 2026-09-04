"""partner_benefits

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-04 09:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: str | Sequence[str] | None = 'd4e5f6a7b8c9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'partner_benefits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label'),
    )

    op.create_table(
        'partner_level_benefits',
        sa.Column('partner_level_id', sa.Integer(), nullable=False),
        sa.Column('partner_benefit_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['partner_level_id'], ['partner_levels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['partner_benefit_id'], ['partner_benefits.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('partner_level_id', 'partner_benefit_id'),
    )

    # `benefits` (texte libre) remplacé par le catalogue `partner_benefits` +
    # la table de liaison ci-dessus, même patron que pass_contents
    # (ROADMAP_PUBLIC_SEO.md Partie 8, demande explicite de l'utilisateur de
    # gérer les avantages de partenariat comme les inclusions de pass).
    op.drop_column('partner_levels', 'benefits')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('partner_levels', sa.Column('benefits', sa.Text(), nullable=True))
    op.drop_table('partner_level_benefits')
    op.drop_table('partner_benefits')
