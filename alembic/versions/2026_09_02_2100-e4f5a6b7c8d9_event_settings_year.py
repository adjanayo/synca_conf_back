"""event_settings year

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-09-02 21:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e4f5a6b7c8d9'
down_revision: str | Sequence[str] | None = 'd3e4f5a6b7c8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('event_settings', sa.Column('year', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('event_settings', 'year')
