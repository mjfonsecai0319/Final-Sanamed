"""Fix/add stripe columns if missing

Revision ID: c_fix_stripe_columns
Revises: b_add_stripe_fields
Create Date: 2025-10-02 00:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'c_fix_stripe_columns'
down_revision = 'b_add_stripe_fields'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns('suscripciones')}
    # Add columns only if missing (handles environments where they already exist)
    if 'stripe_customer_id' not in existing_cols:
        op.add_column('suscripciones', sa.Column('stripe_customer_id', sa.String(length=100), nullable=True))
    if 'stripe_subscription_id' not in existing_cols:
        op.add_column('suscripciones', sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True))
        # Unique constraint only if column now added and constraint not already there
        # Alembic doesn't give direct inspector for constraints by name in cross-DB way; try create and let DB ignore? -> safer: check existing unique constraints
        try:
            op.create_unique_constraint('uq_suscripciones_stripe_subscription_id', 'suscripciones', ['stripe_subscription_id'])
        except Exception:
            # Ignore if already exists
            pass

def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns('suscripciones')}
    # Drop constraint first if present
    try:
        op.drop_constraint('uq_suscripciones_stripe_subscription_id', 'suscripciones', type_='unique')
    except Exception:
        pass
    if 'stripe_subscription_id' in existing_cols:
        try:
            op.drop_column('suscripciones', 'stripe_subscription_id')
        except Exception:
            pass
    if 'stripe_customer_id' in existing_cols:
        try:
            op.drop_column('suscripciones', 'stripe_customer_id')
        except Exception:
            pass
