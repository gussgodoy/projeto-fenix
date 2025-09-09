# /agencia/my_app/__init__.py
from flask import Flask
from flask_cors import CORS
from .db import get_db_connection

def create_app():
    app = Flask(__name__)

    # Alteração: Inicialização explícita do CORS para garantir a aplicação do header
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.route('/health')
    def health_check():
        try:
            conn = get_db_connection()
            conn.close()
            db_status = "OK"
        except Exception as e:
            db_status = f"error: {e}"

        return {
            "app_version": "1.0.0",
            "database_status": db_status,
            "server_status": "OK"
        }

    return app