"""campaign_window_event_key

Revision ID: b1c2d3e4f5a6
Revises: 75418b933d4f
Create Date: 2026-09-02 15:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: str | Sequence[str] | None = '75418b933d4f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'campaign_windows',
        'key',
        existing_type=sa.Enum(
            'call_for_speaker', 'ticketing', 'call_for_partner',
            'call_for_ambassador', 'call_for_exhibitor',
            name='campaign_window_key',
        ),
        type_=sa.Enum(
            'call_for_speaker', 'ticketing', 'call_for_partner',
            'call_for_ambassador', 'call_for_exhibitor', 'event',
            name='campaign_window_key',
        ),
        existing_nullable=False,
    )

    # Seed : dates réelles de la conférence (18-20 août 2027, cf. syncaconf/Infos.md),
    # utilisées pour le compte à rebours public et l'affichage des dates sur le site.
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
                'key': 'event',
                'start_at': '2027-08-18 00:00:00',
                'end_at': '2027-08-20 23:59:59',
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM campaign_windows WHERE `key` = 'event'")
    op.alter_column(
        'campaign_windows',
        'key',
        existing_type=sa.Enum(
            'call_for_speaker', 'ticketing', 'call_for_partner',
            'call_for_ambassador', 'call_for_exhibitor', 'event',
            name='campaign_window_key',
        ),
        type_=sa.Enum(
            'call_for_speaker', 'ticketing', 'call_for_partner',
            'call_for_ambassador', 'call_for_exhibitor',
            name='campaign_window_key',
        ),
        existing_nullable=False,
    )
