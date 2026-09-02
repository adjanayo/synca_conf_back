"""waitlist last_notified_at

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-09-02 20:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd3e4f5a6b7c8'
down_revision: str | Sequence[str] | None = 'c2d3e4f5a6b7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('waitlist', sa.Column('last_notified_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('waitlist', 'last_notified_at')
