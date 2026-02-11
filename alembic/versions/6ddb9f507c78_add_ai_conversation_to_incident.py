"""add_ai_conversation_to_incident"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ddb9f507c78'
down_revision = '8cdba2577e27'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('Incidents', sa.Column('ai_conversation', sa.Text(), nullable=True, doc='Registro de la conversación con la IA.'))


def downgrade():
    op.drop_column('Incidents', 'ai_conversation')
