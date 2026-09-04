"""hackathon_team_is_public

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-04 09:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b8c9d0e1f2a3'
down_revision: str | Sequence[str] | None = 'a7b8c9d0e1f2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'hackathon_teams',
        sa.Column('is_public', sa.Boolean(), server_default='1', nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('hackathon_teams', 'is_public')
