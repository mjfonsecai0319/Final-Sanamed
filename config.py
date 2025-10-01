import os
import re

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sanamed'

    # Configuración de base de datos - MODIFICADO PARA RENDER
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://usuario:sanamed@localhost/postsanamed'
    
    # Arreglar la URL si es necesario
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'sanamed467@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'bkca lkuj cahk rnlm'