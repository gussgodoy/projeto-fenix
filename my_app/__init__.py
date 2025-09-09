# /my_app/__init__.py

from flask import Flask
from flask_cors import CORS
from .db import get_db_connection
from .routes.config_routes import config_bp
from .routes.dashboard import dashboard_bp
from .routes.escritorio_routes import escritorio_bp
from .routes.knowledge_routes import knowledge_bp
from .routes.agente_routes import agente_bp

def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "https://www.fenix.dev.br"}})

    @app.route('/health')
    def health_check():
        try:
            conn = get_db_connection()
            conn.close()
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {e}"
        return jsonify(database_status=db_status)

    # Registra TODOS os blueprints (módulos da API)
    app.register_blueprint(config_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(escritorio_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(agente_bp)

    return app