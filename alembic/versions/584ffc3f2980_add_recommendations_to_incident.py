"""add_recommendations_to_incident"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '584ffc3f2980'
down_revision = '6fcf33a47d4e'
branch_labels = None
depends_on = None


def upgrade():
     op.add_column('Incidents', sa.Column('recommendations', sa.Text(), nullable=True, doc="Recomendaciones para el futuro."))



def downgrade():
    op.drop_column('Incidents', 'recommendations')
