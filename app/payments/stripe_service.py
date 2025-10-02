import os
import stripe
from datetime import datetime, timedelta
from flask import current_app
from ..models import Suscripcion
from ..extensions import db

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')

PLAN_MENSUAL_PRICE_ID = os.getenv('STRIPE_PLAN_PREMIUM_MENSUAL', 'price_mensual_placeholder')
PLAN_ANUAL_PRICE_ID = os.getenv('STRIPE_PLAN_PREMIUM_ANUAL', 'price_anual_placeholder')
BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5000')

class StripePaymentError(Exception):
    pass

def create_checkout_session(user_id: int, periodicidad: str):
    if periodicidad not in ('mensual', 'anual'):
        raise StripePaymentError('Periodicidad inválida')
    price_id = PLAN_MENSUAL_PRICE_ID if periodicidad == 'mensual' else PLAN_ANUAL_PRICE_ID

    try:
        session = stripe.checkout.Session.create(
            success_url=f"{BASE_URL}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/payments/cancel",
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1
            }],
            metadata={'id_usuario': str(user_id), 'periodicidad': periodicidad}
        )
        return session
    except Exception as e:
        raise StripePaymentError(str(e))


def activate_subscription_from_checkout(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        metadata = session.get('metadata', {})
        id_usuario = int(metadata.get('id_usuario')) if metadata.get('id_usuario') else None
        if not id_usuario:
            raise StripePaymentError('Usuario no encontrado en metadata')
        # crear o actualizar suscripción
        sus = Suscripcion.query.filter_by(id_usuario=id_usuario, activa=True, tipo_plan='premium').first()
        now = datetime.utcnow()
        if not sus:
            sus = Suscripcion(
                id_usuario=id_usuario,
                tipo_plan='premium',
                fecha_inicio=now,
                fecha_fin=now + timedelta(days=30 if metadata.get('periodicidad')=='mensual' else 365),
                activa=True,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id
            )
            db.session.add(sus)
        else:
            sus.fecha_fin = now + timedelta(days=30 if metadata.get('periodicidad')=='mensual' else 365)
            sus.stripe_customer_id = customer_id
            sus.stripe_subscription_id = subscription_id
        db.session.commit()
        return sus
    except Exception as e:
        db.session.rollback()
        raise StripePaymentError(str(e))


def deactivate_subscription(stripe_subscription_id: str):
    """Marca una suscripción local como inactiva cuando Stripe la cancela o falla pago."""
    if not stripe_subscription_id:
        return False
    try:
        sus = Suscripcion.query.filter_by(stripe_subscription_id=stripe_subscription_id, activa=True).first()
        if not sus:
            return False
        sus.activa = False
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
