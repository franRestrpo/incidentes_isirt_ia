"""update_incident_severity_enum"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7135af6d7b0'
down_revision = '6ddb9f507c78'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE incidentseverity ADD VALUE IF NOT EXISTS '-- Evaluar según matriz --'")


def downgrade():
    # No se puede eliminar un valor de un ENUM en PostgreSQL de forma sencilla.
    # La operación de downgrade no es soportada para esta migración.
    pass
