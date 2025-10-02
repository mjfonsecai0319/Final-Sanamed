import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

# Modelo ligero de conversación (puedes cambiar por otro de HuggingFace)
MODEL_URL = os.getenv('HF_CHAT_MODEL_URL', 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-small')

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

FALLBACK_RESPUESTAS = [
    "Estoy aquí para acompañarte. ¿Quieres contarme un poco más?",
    "Entiendo. ¿Cómo crees que podrías afrontarlo?",
    "Gracias por compartirlo. ¿Qué te haría sentir un poco mejor ahora?",
    "Respira profundo. Estoy contigo."
]

import random

def generar_respuesta(mensaje: str):
    if not HF_TOKEN:
        return random.choice(FALLBACK_RESPUESTAS)
    try:
        payload = {"inputs": mensaje}
        r = requests.post(MODEL_URL, headers=HEADERS, json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                posible = data[0].get('generated_text') or ''
                return posible.strip() or random.choice(FALLBACK_RESPUESTAS)
            elif isinstance(data, dict):
                return data.get('generated_text', random.choice(FALLBACK_RESPUESTAS))
        return random.choice(FALLBACK_RESPUESTAS)
    except Exception:
        return random.choice(FALLBACK_RESPUESTAS)
