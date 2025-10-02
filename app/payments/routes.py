from flask import request, redirect, url_for, flash, session, jsonify
from . import payments_bp
from .stripe_service import (
    create_checkout_session,
    activate_subscription_from_checkout,
    deactivate_subscription,
    StripePaymentError
)
import os, stripe, json

STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

@payments_bp.route('/payments/checkout/<plan>')
def checkout(plan):
    if 'id_usuario' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('auth.login'))
    try:
        ses = create_checkout_session(session['id_usuario'], plan)
        return redirect(ses.url)
    except StripePaymentError as e:
        flash(f'Error iniciando pago: {e}', 'error')
        return redirect(url_for('user.upgrade'))

@payments_bp.route('/payments/success')
def success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Sesión de pago no encontrada', 'error')
        return redirect(url_for('user.upgrade'))
    try:
        activate_subscription_from_checkout(session_id)
        flash('¡Pago exitoso! Ya eres Premium.', 'success')
    except StripePaymentError as e:
        flash(f'No se pudo activar la suscripción: {e}', 'error')
    return redirect(url_for('user.upgrade'))

@payments_bp.route('/payments/cancel')
def cancel():
    flash('Pago cancelado.', 'info')
    return redirect(url_for('user.upgrade'))


@payments_bp.route('/payments/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    event = None
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=STRIPE_WEBHOOK_SECRET
            )
        else:
            # Sin secret (entorno dev) intentar parsear directamente
            event = request.get_json()
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    event_type = event.get('type') if isinstance(event, dict) else getattr(event, 'type', None)
    data_object = event.get('data', {}).get('object', {}) if isinstance(event, dict) else event.data.object

    if event_type == 'checkout.session.completed':
        session_id = data_object.get('id')
        try:
            activate_subscription_from_checkout(session_id)
        except Exception:
            pass
    elif event_type in ('customer.subscription.deleted', 'invoice.payment_failed', 'customer.subscription.updated'):
        sub_id = data_object.get('id') if 'subscription' not in data_object else data_object.get('subscription')
        deactivate_subscription(sub_id)

    return jsonify({'status': 'received'})
