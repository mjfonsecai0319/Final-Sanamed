"""add stripe fields

Revision ID: b_add_stripe_fields
Revises: ad7a92fa242e
Create Date: 2025-10-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = 'b_add_stripe_fields'
down_revision = 'ad7a92fa242e'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns('suscripciones')}

    # Añadir sólo si falta
    if 'stripe_customer_id' not in existing_cols:
        op.add_column('suscripciones', sa.Column('stripe_customer_id', sa.String(length=100), nullable=True))

    if 'stripe_subscription_id' not in existing_cols:
        op.add_column('suscripciones', sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True))
        try:
            op.create_unique_constraint('uq_suscripciones_stripe_subscription_id', 'suscripciones', ['stripe_subscription_id'])
        except Exception:
            pass  # constraint puede existir ya
    else:
        # La columna existe; asegurar constraint (ignorar error si ya existe)
        try:
            op.create_unique_constraint('uq_suscripciones_stripe_subscription_id', 'suscripciones', ['stripe_subscription_id'])
        except Exception:
            pass


def downgrade():
    # Intentar eliminar constraint y columnas si existen
    try:
        op.drop_constraint('uq_suscripciones_stripe_subscription_id', 'suscripciones', type_='unique')
    except Exception:
        pass
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_cols = {c['name'] for c in inspector.get_columns('suscripciones')}
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
