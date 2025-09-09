from flask import Flask
from flask_cors import CORS
from .db import get_db_connection

# Importa o nosso novo blueprint unificado de configurações
from .routes.config_routes import config_bp

def create_app():
    app = Flask(__name__)
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

    # Registra o blueprint unificado na aplicação
    app.register_blueprint(config_bp)

    return app