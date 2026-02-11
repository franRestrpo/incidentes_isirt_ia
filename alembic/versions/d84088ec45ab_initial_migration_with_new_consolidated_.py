"""Initial migration with new consolidated structure"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd84088ec45ab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Manually Adjusted Alembic Commands ###

    # Create tables with no dependencies first
    op.create_table('groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_groups_id'), 'groups', ['id'], unique=False)
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)

    op.create_table('ai_model_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('system_prompt', sa.String(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_model_settings_id'), 'ai_model_settings', ['id'], unique=False)

    op.create_table('available_ai_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name')
    )
    op.create_index(op.f('ix_available_ai_models_id'), 'available_ai_models', ['id'], unique=False)
    op.create_index(op.f('ix_available_ai_models_provider'), 'available_ai_models', ['provider'], unique=False)

    op.create_table('IncidentClassifications',
        sa.Column('classification_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('classification_id')
    )
    op.create_index(op.f('ix_IncidentClassifications_classification_id'), 'IncidentClassifications', ['classification_id'], unique=False)

    # Create tables that depend on the ones above
    op.create_table('Users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('EMPLEADO', 'MIEMBRO_IRT', 'LIDER_IRT', 'ADMINISTRADOR', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_Users_email'), 'Users', ['email'], unique=True)
    op.create_index(op.f('ix_Users_user_id'), 'Users', ['user_id'], unique=False)

    op.create_table('Incidents',
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.String(length=20), nullable=False),
        sa.Column('reported_by_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('classification_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('NUEVO', 'INVESTIGANDO', 'CONTENIDO', 'ERRADICADO', 'RECUPERANDO', 'RESUELTO', 'CERRADO', name='incidentstatus'), nullable=False),
        sa.Column('severity', sa.Enum('SEV1', 'SEV2', 'SEV3', 'SEV4', name='incidentseverity'), nullable=True),
        sa.Column('discovery_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('summary', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('root_cause_analysis', sa.Text(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('corrective_actions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('impact_scores', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['Users.user_id'], ),
        sa.ForeignKeyConstraint(['classification_id'], ['IncidentClassifications.classification_id'], ),
        sa.ForeignKeyConstraint(['reported_by_id'], ['Users.user_id'], ),
        sa.PrimaryKeyConstraint('incident_id')
    )
    op.create_index(op.f('ix_Incidents_incident_id'), 'Incidents', ['incident_id'], unique=False)
    op.create_index(op.f('ix_Incidents_ticket_id'), 'Incidents', ['ticket_id'], unique=True)

    # Create tables with the most dependencies last
    op.create_table('EvidenceFiles',
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['Incidents.incident_id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['Users.user_id'], ),
        sa.PrimaryKeyConstraint('file_id')
    )
    op.create_index(op.f('ix_EvidenceFiles_file_id'), 'EvidenceFiles', ['file_id'], unique=False)

    op.create_table('IncidentLog',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('field_modified', sa.String(length=100), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['Incidents.incident_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_IncidentLog_log_id'), 'IncidentLog', ['log_id'], unique=False)

    op.create_table('incident_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('field_changed', sa.String(), nullable=False),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=True),
        sa.Column('details', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['Incidents.incident_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_history_id'), 'incident_history', ['id'], unique=False)

    op.create_table('conversation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('message_content', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['Users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_history_id'), 'conversation_history', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_history_conversation_id'), 'conversation_history', ['conversation_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### Manually Adjusted Alembic Commands ###
    op.drop_table('conversation_history')
    op.drop_table('incident_history')
    op.drop_table('IncidentLog')
    op.drop_table('EvidenceFiles')
    op.drop_table('Incidents')
    op.drop_table('Users')
    op.drop_table('IncidentClassifications')
    op.drop_table('available_ai_models')
    op.drop_table('ai_model_settings')
    op.drop_table('groups')
    # ### end Alembic commands ###