# /my_app/__init__.py

from flask import Flask
from flask_cors import CORS  # --- ADICIONE ESTA LINHA ---
from .db import get_db_connection
from .routes.config_routes import config_bp
from .routes.dashboard import dashboard_bp
from .routes.escritorio_routes import escritorio_bp

def create_app():
    app = Flask(__name__)

    # --- CONFIGURAÇÃO DE CORS ADICIONADA ---
    # Permite que o frontend em 'https://www.fenix.dev.br' acesse todas as rotas da API.
    CORS(app, resources={r"/api/*": {"origins": "https://www.fenix.dev.br"}})
    # -------------------------------------

    @app.route('/health')
    def health_check():
        try:
            conn = get_db_connection()
            conn.close()
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {e}"
        return jsonify(database_status=db_status)

    app.register_blueprint(config_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(escritorio_bp)

    return app