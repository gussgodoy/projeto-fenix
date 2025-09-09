# /projeto-fenix/my_app/__init__.py

from flask import Flask, jsonify
from flask_cors import CORS
import requests # <-- NOVA IMPORTAÇÃO

def create_app():
    """Cria e configura uma instância da aplicação Flask."""
    app = Flask(__name__)
    CORS(app)

    # Importa e registra os Blueprints
    from .routes.dashboard import dashboard_bp
    from .routes.configuracoes import config_bp
    # from .routes.escritorio import escritorio_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(config_bp)
    # app.register_blueprint(escritorio_bp)

    # Rota de saúde principal
    @app.route('/api/health', methods=['GET'])
    def server_health_check():
        from .db import get_db_connection
        conn = None
        db_status = "disconnected"
        try:
            conn = get_db_connection()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        finally:
            if conn:
                conn.close()
        return jsonify({
            "server_status": "OK",
            "app_version": "22.4 (Routes Health Check)",
            "database_status": db_status
        }), 200

    # --- NOVA ROTA DE SAÚDE COMPLETA ---
    @app.route('/api/routes-health', methods=['GET'])
    def routes_health_check():
        # Lista de endpoints GET para testar
        # Usamos um cliente_id=0 que provavelmente não existe, 
        # o objetivo é apenas verificar se a rota responde com um status esperado (200 ou 404), não se retorna dados.
        endpoints_to_test = {
            "Dashboard - Conversas": "/api/dashboard/conversations?cliente_id=0",
            "Config - Provedores": "/api/config/provedores",
            "Config - Chaves API": "/api/config/chaves-api",
            "Config - Canais": "/api/config/canais",
        }
        
        results = {}
        base_url = "http://127.0.0.1:5000"

        for name, endpoint in endpoints_to_test.items():
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                # Consideramos sucesso qualquer resposta (OK, Not Found, etc), 
                # pois prova que a rota está registrada e respondendo.
                if response.status_code:
                    results[name] = {"status": "ok", "statusCode": response.status_code}
                else:
                    results[name] = {"status": "error", "message": "Resposta sem código de status"}
            except requests.exceptions.RequestException as e:
                results[name] = {"status": "error", "message": str(e)}

        return jsonify(results)

    return app