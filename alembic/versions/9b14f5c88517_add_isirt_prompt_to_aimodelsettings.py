"""Add isirt_prompt to AIModelSettings"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b14f5c88517'
down_revision = '58e713d9aa78'
branch_labels = None
depends_on = None


def upgrade():
    # Paso 1: Añadir la columna permitiendo nulos temporalmente
    op.add_column('ai_model_settings', sa.Column('isirt_prompt', sa.String(), nullable=True))

    # Paso 2: Rellenar la columna en las filas existentes con un valor por defecto
    default_prompt = "Eres un asistente de IA experto en ciberseguridad para el equipo de respuesta a incidentes (ISIRT). Basa tus respuestas únicamente en el contexto de los playbooks proporcionados."
    op.execute(
        sa.text("UPDATE ai_model_settings SET isirt_prompt = :default_prompt").bindparams(default_prompt=default_prompt)
    )

    # Paso 3: Alterar la columna para que no permita nulos
    op.alter_column('ai_model_settings', 'isirt_prompt', nullable=False)


def downgrade():
    op.drop_column('ai_model_settings', 'isirt_prompt')
