# /agencia/my_app/__init__.py

from flask import Flask
from flask_cors import CORS
from .db import get_db_connection

# Importa o nosso blueprint de rotas de IA
from .routes.ia_config import ia_bp

def create_app():
    app = Flask(__name__)
    
    # Configuração explícita do CORS para máxima compatibilidade
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

    # Registra o blueprint na aplicação, tornando as rotas de IA ativas
    app.register_blueprint(ia_bp)

    return app