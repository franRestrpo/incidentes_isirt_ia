"""add_new_severity_values"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fcf33a47d4e'
down_revision = 'c7135af6d7b0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE incidentseverity ADD VALUE IF NOT EXISTS 'SEV-1 (Crítico)'")
    op.execute("ALTER TYPE incidentseverity ADD VALUE IF NOT EXISTS 'SEV-2 (Alto)'")
    op.execute("ALTER TYPE incidentseverity ADD VALUE IF NOT EXISTS 'SEV-3 (Medio)'")
    op.execute("ALTER TYPE incidentseverity ADD VALUE IF NOT EXISTS 'SEV-4 (Bajo)'") 


def downgrade():
    pass