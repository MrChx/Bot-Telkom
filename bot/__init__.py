from flask import Flask
from config import Config

def create_app():
    # Buat instance Flask
    app = Flask(__name__)
    
    # Terapkan konfigurasi dari config.py
    app.config.from_object(Config)
    
    # Impor blueprint/route jika diperlukan
    from . import routes
    
    return app