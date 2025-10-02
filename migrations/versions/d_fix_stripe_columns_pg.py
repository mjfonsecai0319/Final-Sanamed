"""Ensure stripe columns exist (PostgreSQL specific)

Revision ID: d_fix_stripe_columns_pg
Revises: c_fix_stripe_columns
Create Date: 2025-10-02 00:45:00.000000
"""
from alembic import op

revision = 'd_fix_stripe_columns_pg'
down_revision = 'c_fix_stripe_columns'
branch_labels = None
depends_on = None

CHECK_AND_ADD_SQL = """
DO $$
BEGIN
    -- stripe_customer_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='suscripciones' AND column_name='stripe_customer_id'
    ) THEN
        ALTER TABLE suscripciones ADD COLUMN stripe_customer_id VARCHAR(100);
    END IF;

    -- stripe_subscription_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='suscripciones' AND column_name='stripe_subscription_id'
    ) THEN
        ALTER TABLE suscripciones ADD COLUMN stripe_subscription_id VARCHAR(100);
    END IF;

    -- unique constraint
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name='suscripciones' AND constraint_name='uq_suscripciones_stripe_subscription_id'
    ) THEN
        ALTER TABLE suscripciones ADD CONSTRAINT uq_suscripciones_stripe_subscription_id UNIQUE (stripe_subscription_id);
    END IF;
END$$;
"""


def upgrade():
    op.execute(CHECK_AND_ADD_SQL)


def downgrade():
    # Downgrade: quitar constraint y columnas si existen
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE table_name='suscripciones' AND constraint_name='uq_suscripciones_stripe_subscription_id'
        ) THEN
            ALTER TABLE suscripciones DROP CONSTRAINT uq_suscripciones_stripe_subscription_id;
        END IF;
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='suscripciones' AND column_name='stripe_subscription_id') THEN
            ALTER TABLE suscripciones DROP COLUMN stripe_subscription_id;
        END IF;
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_name='suscripciones' AND column_name='stripe_customer_id') THEN
            ALTER TABLE suscripciones DROP COLUMN stripe_customer_id;
        END IF;
    END$$;
    """)
