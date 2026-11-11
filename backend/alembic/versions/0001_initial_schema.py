"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-11-11 20:52:00.998341
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reviewed initial schema (LLD 6.2).
    op.create_table('accounts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_accounts')),
    sa.UniqueConstraint('email', name=op.f('uq_accounts_email'))
    )
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.create_index('ix_accounts_email', ['email'], unique=False)

    op.create_table('alert_rules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('identifier', sa.String(length=64), nullable=False),
    sa.Column('version', sa.String(length=32), nullable=False),
    sa.Column('metric_type', sa.String(length=64), nullable=False),
    sa.Column('definition', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
    sa.Column('content_template', sa.String(length=1000), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_alert_rules')),
    sa.UniqueConstraint('identifier', name=op.f('uq_alert_rules_identifier'))
    )
    op.create_table('audit_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=True),
    sa.Column('correlation_id', sa.String(length=128), nullable=False),
    sa.Column('event_type', sa.String(length=64), nullable=False),
    sa.Column('severity', sa.String(length=16), nullable=False),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('entity_id', sa.Uuid(), nullable=True),
    sa.Column('metadata', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_audit_logs_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.create_index('ix_audit_account_occurred', ['account_id', 'occurred_at'], unique=False)
        batch_op.create_index('ix_audit_correlation', ['correlation_id'], unique=False)

    op.create_table('connections',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('source', sa.String(length=16), nullable=False),
    sa.Column('provider', sa.String(length=64), nullable=False),
    sa.Column('external_identifier', sa.String(length=128), nullable=False),
    sa.Column('display_label', sa.String(length=100), nullable=False),
    sa.Column('authorization_state', sa.String(length=24), nullable=False),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('last_successful_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_failure_code', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("authorization_state IN ('pending','authorized','failed','revoked')", name=op.f('ck_connections_authorization_state')),
    sa.CheckConstraint("source IN ('scale','wearable')", name=op.f('ck_connections_source')),
    sa.CheckConstraint("status IN ('pending','current','stale','failed','disconnected')", name=op.f('ck_connections_status')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_connections_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_connections')),
    sa.UniqueConstraint('account_id', 'source', 'provider', 'external_identifier', name='uq_connections_device')
    )
    with op.batch_alter_table('connections', schema=None) as batch_op:
        batch_op.create_index('ix_connections_account_status', ['account_id', 'status'], unique=False)

    op.create_table('consent_records',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('decision', sa.String(length=16), nullable=False),
    sa.Column('notice_version', sa.String(length=64), nullable=False),
    sa.Column('data_categories', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=False),
    sa.Column('purpose', sa.String(length=64), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("decision IN ('granted','withdrawn')", name=op.f('ck_consent_records_decision')),
    sa.CheckConstraint("purpose = 'wellness_support'", name=op.f('ck_consent_records_purpose')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_consent_records_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_consent_records'))
    )
    with op.batch_alter_table('consent_records', schema=None) as batch_op:
        batch_op.create_index('ix_consent_records_account_recorded', ['account_id', 'recorded_at'], unique=False)

    op.create_table('data_rights_requests',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('reference', sa.String(length=40), nullable=False),
    sa.Column('request_type', sa.String(length=16), nullable=False),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('fulfillment_due_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("request_type IN ('export','deletion')", name=op.f('ck_data_rights_requests_request_type')),
    sa.CheckConstraint("status IN ('submitted','in_review','fulfilled','rejected')", name=op.f('ck_data_rights_requests_status')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_data_rights_requests_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_data_rights_requests')),
    sa.UniqueConstraint('reference', name=op.f('uq_data_rights_requests_reference'))
    )
    with op.batch_alter_table('data_rights_requests', schema=None) as batch_op:
        batch_op.create_index('ix_rights_requests_account_requested', ['account_id', 'requested_at'], unique=False)

    op.create_table('insights',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('metric_type', sa.String(length=64), nullable=False),
    sa.Column('observation_period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('observation_period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('observation', sa.String(length=1000), nullable=False),
    sa.Column('wellness_guidance', sa.String(length=1000), nullable=False),
    sa.Column('uncertainty', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_insights_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_insights'))
    )
    with op.batch_alter_table('insights', schema=None) as batch_op:
        batch_op.create_index('ix_insights_account_created', ['account_id', 'created_at'], unique=False)

    op.create_table('sessions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('token_hash', sa.String(length=128), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_sessions_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sessions')),
    sa.UniqueConstraint('token_hash', name=op.f('uq_sessions_token_hash'))
    )
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.create_index('ix_sessions_account_active', ['account_id', 'revoked_at', 'expires_at'], unique=False)

    op.create_table('support_requests',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('reference', sa.String(length=40), nullable=False),
    sa.Column('category', sa.String(length=32), nullable=False),
    sa.Column('description', sa.String(length=2000), nullable=False),
    sa.Column('context_type', sa.String(length=16), nullable=False),
    sa.Column('context_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("category IN ('connection','data_quality','account','alert')", name=op.f('ck_support_requests_category')),
    sa.CheckConstraint("context_type IN ('device','account','alert')", name=op.f('ck_support_requests_context_type')),
    sa.CheckConstraint("status = 'submitted'", name=op.f('ck_support_requests_status')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_support_requests_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_support_requests')),
    sa.UniqueConstraint('reference', name=op.f('uq_support_requests_reference'))
    )
    with op.batch_alter_table('support_requests', schema=None) as batch_op:
        batch_op.create_index('ix_support_account_submitted', ['account_id', 'submitted_at'], unique=False)

    op.create_table('wellness_goals',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('category', sa.String(length=32), nullable=False),
    sa.Column('metric_type', sa.String(length=64), nullable=False),
    sa.Column('target_value', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('target_unit', sa.String(length=32), nullable=False),
    sa.Column('target_date', sa.Date(), nullable=False),
    sa.Column('state', sa.String(length=16), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("category IN ('weight_management','fitness','sleep_improvement','general_wellness')", name=op.f('ck_wellness_goals_category')),
    sa.CheckConstraint("state IN ('active','paused','closed')", name=op.f('ck_wellness_goals_state')),
    sa.CheckConstraint('target_value > 0', name=op.f('ck_wellness_goals_target_value')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_wellness_goals_account_id_accounts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_wellness_goals'))
    )
    with op.batch_alter_table('wellness_goals', schema=None) as batch_op:
        batch_op.create_index('ix_goals_account_state', ['account_id', 'state'], unique=False)

    op.create_table('insight_feedback',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('insight_id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('useful', sa.Boolean(), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_insight_feedback_account_id_accounts')),
    sa.ForeignKeyConstraint(['insight_id'], ['insights.id'], name=op.f('fk_insight_feedback_insight_id_insights')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_insight_feedback')),
    sa.UniqueConstraint('insight_id', 'account_id', name='uq_insight_feedback_owner')
    )
    op.create_table('reading_processing_outcomes',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('connection_id', sa.Uuid(), nullable=True),
    sa.Column('idempotency_key', sa.String(length=128), nullable=True),
    sa.Column('outcome', sa.String(length=16), nullable=False),
    sa.Column('reason_code', sa.String(length=64), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("outcome IN ('accepted','rejected','duplicate')", name=op.f('ck_reading_processing_outcomes_outcome')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_reading_processing_outcomes_account_id_accounts')),
    sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], name=op.f('fk_reading_processing_outcomes_connection_id_connections')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_reading_processing_outcomes'))
    )
    with op.batch_alter_table('reading_processing_outcomes', schema=None) as batch_op:
        batch_op.create_index('ix_reading_outcomes_account_occurred', ['account_id', 'occurred_at'], unique=False)

    op.create_table('readings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('connection_id', sa.Uuid(), nullable=True),
    sa.Column('metric_type', sa.String(length=64), nullable=False),
    sa.Column('value', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('unit', sa.String(length=32), nullable=False),
    sa.Column('source', sa.String(length=16), nullable=False),
    sa.Column('captured_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('idempotency_key', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("source IN ('manual','scale','wearable')", name=op.f('ck_readings_source')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_readings_account_id_accounts')),
    sa.ForeignKeyConstraint(['connection_id'], ['connections.id'], name=op.f('fk_readings_connection_id_connections')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_readings')),
    sa.UniqueConstraint('account_id', 'source', 'idempotency_key', name='uq_readings_idempotency')
    )
    with op.batch_alter_table('readings', schema=None) as batch_op:
        batch_op.create_index('ix_readings_connection_capture', ['connection_id', 'captured_at'], unique=False)
        batch_op.create_index('ix_readings_owner_metric_capture', ['account_id', 'metric_type', 'captured_at'], unique=False)

    op.create_table('wellness_alerts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('alert_rule_id', sa.Uuid(), nullable=False),
    sa.Column('source_reading_id', sa.Uuid(), nullable=False),
    sa.Column('metric_type', sa.String(length=64), nullable=False),
    sa.Column('event_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('reason', sa.String(length=1000), nullable=False),
    sa.Column('state', sa.String(length=16), nullable=False),
    sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("state IN ('active','acknowledged')", name=op.f('ck_wellness_alerts_state')),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_wellness_alerts_account_id_accounts')),
    sa.ForeignKeyConstraint(['alert_rule_id'], ['alert_rules.id'], name=op.f('fk_wellness_alerts_alert_rule_id_alert_rules')),
    sa.ForeignKeyConstraint(['source_reading_id'], ['readings.id'], name=op.f('fk_wellness_alerts_source_reading_id_readings')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_wellness_alerts')),
    sa.UniqueConstraint('account_id', 'alert_rule_id', 'source_reading_id', 'state', name='uq_alerts_dedup')
    )
    with op.batch_alter_table('wellness_alerts', schema=None) as batch_op:
        batch_op.create_index('ix_alerts_account_state_event', ['account_id', 'state', 'event_at'], unique=False)

    op.create_table('alert_acknowledgements',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('alert_id', sa.Uuid(), nullable=False),
    sa.Column('account_id', sa.Uuid(), nullable=False),
    sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name=op.f('fk_alert_acknowledgements_account_id_accounts')),
    sa.ForeignKeyConstraint(['alert_id'], ['wellness_alerts.id'], name=op.f('fk_alert_acknowledgements_alert_id_wellness_alerts')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_alert_acknowledgements')),
    sa.UniqueConstraint('alert_id', 'account_id', name='uq_alert_ack_owner')
    )
    with op.batch_alter_table('alert_acknowledgements', schema=None) as batch_op:
        batch_op.create_index('ix_alert_ack_account_time', ['account_id', 'acknowledged_at'], unique=False)



def downgrade() -> None:
    # Reviewed initial schema (LLD 6.2).
    with op.batch_alter_table('alert_acknowledgements', schema=None) as batch_op:
        batch_op.drop_index('ix_alert_ack_account_time')

    op.drop_table('alert_acknowledgements')
    with op.batch_alter_table('wellness_alerts', schema=None) as batch_op:
        batch_op.drop_index('ix_alerts_account_state_event')

    op.drop_table('wellness_alerts')
    with op.batch_alter_table('readings', schema=None) as batch_op:
        batch_op.drop_index('ix_readings_owner_metric_capture')
        batch_op.drop_index('ix_readings_connection_capture')

    op.drop_table('readings')
    with op.batch_alter_table('reading_processing_outcomes', schema=None) as batch_op:
        batch_op.drop_index('ix_reading_outcomes_account_occurred')

    op.drop_table('reading_processing_outcomes')
    op.drop_table('insight_feedback')
    with op.batch_alter_table('wellness_goals', schema=None) as batch_op:
        batch_op.drop_index('ix_goals_account_state')

    op.drop_table('wellness_goals')
    with op.batch_alter_table('support_requests', schema=None) as batch_op:
        batch_op.drop_index('ix_support_account_submitted')

    op.drop_table('support_requests')
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_index('ix_sessions_account_active')

    op.drop_table('sessions')
    with op.batch_alter_table('insights', schema=None) as batch_op:
        batch_op.drop_index('ix_insights_account_created')

    op.drop_table('insights')
    with op.batch_alter_table('data_rights_requests', schema=None) as batch_op:
        batch_op.drop_index('ix_rights_requests_account_requested')

    op.drop_table('data_rights_requests')
    with op.batch_alter_table('consent_records', schema=None) as batch_op:
        batch_op.drop_index('ix_consent_records_account_recorded')

    op.drop_table('consent_records')
    with op.batch_alter_table('connections', schema=None) as batch_op:
        batch_op.drop_index('ix_connections_account_status')

    op.drop_table('connections')
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_index('ix_audit_correlation')
        batch_op.drop_index('ix_audit_account_occurred')

    op.drop_table('audit_logs')
    op.drop_table('alert_rules')
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_index('ix_accounts_email')

    op.drop_table('accounts')
