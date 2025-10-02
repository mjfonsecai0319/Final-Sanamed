from flask import request, jsonify, session
from datetime import datetime, date
from . import chatbot_bp
from ..models import ChatbotMensaje, Suscripcion
from ..extensions import db
from .ai_service import generar_respuesta

LIMITE_GRATUITO_DIARIO = 15

@chatbot_bp.route('/api/chatbot/mensaje', methods=['POST'])
def enviar_mensaje_chatbot():
    if 'id_usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    data = request.get_json() or {}
    mensaje = data.get('mensaje', '').strip()
    if not mensaje:
        return jsonify({'error': 'Mensaje vacío'}), 400

    id_usuario = session['id_usuario']
    hoy = date.today()

    es_premium = Suscripcion.usuario_es_premium(id_usuario)

    if not es_premium:
        usados_hoy = ChatbotMensaje.query.filter(
            ChatbotMensaje.id_usuario == id_usuario,
            ChatbotMensaje.fecha >= datetime(hoy.year, hoy.month, hoy.day)
        ).count()
        if usados_hoy >= LIMITE_GRATUITO_DIARIO:
            return jsonify({
                'error': 'limite',
                'mensaje': 'Has alcanzado el límite diario gratuito. Mejora a Premium para uso ilimitado.'
            }), 402

    respuesta = generar_respuesta(mensaje)

    registro = ChatbotMensaje(
        id_usuario=id_usuario,
        mensaje_usuario=mensaje,
        respuesta_bot=respuesta,
        es_premium=es_premium
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify({
        'respuesta': respuesta,
        'es_premium': es_premium
    })

@chatbot_bp.route('/api/chatbot/estado', methods=['GET'])
def estado_chatbot():
    if 'id_usuario' not in session:
        return jsonify({'autenticado': False})
    id_usuario = session['id_usuario']
    es_premium = Suscripcion.usuario_es_premium(id_usuario)
    hoy = date.today()
    usados_hoy = ChatbotMensaje.query.filter(
        ChatbotMensaje.id_usuario == id_usuario,
        ChatbotMensaje.fecha >= datetime(hoy.year, hoy.month, hoy.day)
    ).count()
    return jsonify({
        'autenticado': True,
        'es_premium': es_premium,
        'limite': LIMITE_GRATUITO_DIARIO,
        'usados_hoy': usados_hoy
    })
