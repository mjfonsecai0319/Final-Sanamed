from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .extensions import db

class Perfil(db.Model):
    __tablename__ = 'perfiles'
    id_perfil = db.Column(db.Integer, primary_key=True)
    tipo_perfil = db.Column(db.String(20), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo_documento = db.Column(db.String(20), nullable=False)
    numero_documento = db.Column(db.String(20), unique=True, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    tipo_perfil = db.Column(db.String(20), nullable=False, default='usuario')
    reset_token = db.Column(db.String(100), nullable=True)  # Token para restablecer contraseña

class Profesional(db.Model):
    __tablename__ = 'profesionales'
    id_profesional = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    especialidad = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)  # Token para restablecer contraseña


class Administrador(db.Model):
    __tablename__ = 'administradores'
    id_administrador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)  # Token para restablecer contraseña
    
class Consulta(db.Model):
    __tablename__ = 'consultas'
    id_consulta = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_profesional = db.Column(db.Integer, db.ForeignKey('profesionales.id_profesional'))
    fecha_consulta = db.Column(db.Date, nullable=False)
    hora_consulta = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    estado = db.Column(db.String(20), default='Pendiente')


class Emocion(db.Model):
    __tablename__ = 'emociones'
    id_emocion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha_emocion = db.Column(db.DateTime, default=datetime.utcnow)
    emocion = db.Column(db.String(20), nullable=False)

class ProfesionalUsuario(db.Model):
    __tablename__ = 'profesionales_usuarios'
    id_profesional = db.Column(db.Integer, db.ForeignKey('profesionales.id_profesional'), primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), primary_key=True)
    
    
class FamiliaGratitud(db.Model):
    __tablename__ = 'familias_gratitud'
    id_gratitud = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    gratitud = db.Column(db.String(500), nullable=False)  # Longitud adecuada para textos
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices para mejor performance
    __table_args__ = (
        db.Index('idx_familia_gratitud_usuario', 'id_usuario'),
    )

# ---------------- Nuevos modelos para funcionalidad Chatbot Premium ----------------

class Suscripcion(db.Model):
    __tablename__ = 'suscripciones'
    id_suscripcion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False, index=True)
    tipo_plan = db.Column(db.String(20), nullable=False, default='gratuito')  # gratuito | premium
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    activa = db.Column(db.Boolean, default=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True, unique=True)

    __table_args__ = (
        db.Index('idx_suscripcion_usuario_activa', 'id_usuario', 'activa'),
    )

    @staticmethod
    def usuario_es_premium(id_usuario: int) -> bool:
        from datetime import datetime as _dt
        ahora = _dt.utcnow()
        sus = Suscripcion.query.filter(
            Suscripcion.id_usuario == id_usuario,
            Suscripcion.activa.is_(True),
            Suscripcion.tipo_plan == 'premium',
            db.or_(Suscripcion.fecha_fin.is_(None), Suscripcion.fecha_fin > ahora)
        ).first()
        return sus is not None


class ChatbotMensaje(db.Model):
    __tablename__ = 'chatbot_mensajes'
    id_mensaje = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False, index=True)
    mensaje_usuario = db.Column(db.Text, nullable=False)
    respuesta_bot = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    es_premium = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.Index('idx_chatbot_usuario_fecha', 'id_usuario', 'fecha'),
    )

