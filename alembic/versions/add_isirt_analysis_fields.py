"""add_isirt_analysis_fields

Revision ID: add_isirt_001
Revises: [latest_revision_id]
Create Date: 2025-09-14 21:21:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_isirt_001'
down_revision: Union[str, None] = '5f8b61ae0c33'  # Replace with actual previous revision
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ISIRT analysis fields to incidents table."""
    # Add new columns for ISIRT analysis
    op.add_column('Incidents', sa.Column('containment_actions', sa.Text(), nullable=True))
    op.add_column('Incidents', sa.Column('recovery_actions', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove ISIRT analysis fields from incidents table."""
    # Remove the added columns
    op.drop_column('Incidents', 'recovery_actions')
    op.drop_column('Incidents', 'containment_actions')