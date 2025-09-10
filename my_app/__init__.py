# /my_app/__init__.py

from flask import Flask
from flask_cors import CORS
from .db import get_db_connection
from flask import jsonify # Certifique-se de que jsonify está importado

# Importação de todos os blueprints
from .routes.config_routes import config_bp
from .routes.dashboard import dashboard_bp
from .routes.escritorio_routes import escritorio_bp
from .routes.knowledge_routes import knowledge_bp
from .routes.agente_routes import agente_bp

def create_app():
    app = Flask(__name__)

    # Configuração do CORS
    CORS(app, resources={r"/api/*": {"origins": "https://www.fenix.dev.br"}})

    # ROTA DE SAÚDE PRINCIPAL (agora no sítio correto)
    @app.route('/health')
    def health_check():
        db_status = "ok"
        try:
            conn = get_db_connection()
            conn.close()
        except Exception as e:
            db_status = f"error: {e}"
        
        return jsonify(
            server_status="OK",
            database_status=db_status
        )

    # Registro de todos os blueprints
    app.register_blueprint(config_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(escritorio_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(agente_bp)

    return app