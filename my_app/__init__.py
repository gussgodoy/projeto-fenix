# /agencia/my_app/__init__.py
from flask import Flask
from .db import get_db_connection # Importa a função de conexão

def create_app():
    app = Flask(__name__)

    # Rota de teste para saúde do sistema
    @app.route('/health')
    def health_check():
        try:
            # Tenta conectar ao banco para validar a conexão
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

    # Adicione aqui o registo de outras rotas (Blueprints) no futuro
    # from .routes import seu_blueprint
    # app.register_blueprint(seu_blueprint)

    return app