# my_app/__init__.py

from flask import Flask
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)

    # Configurações do App
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_padrao_para_desenvolvimento')

    # Importar e Registrar Blueprints das Rotas
    from .routes.status_routes import status_bp
    from .routes.key_routes import key_bp
    from .routes.provider_routes import provider_bp
    from .routes.client_routes import client_bp
    from .routes.knowledge_routes import knowledge_bp
    from .routes.agent_routes import agent_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(status_bp, url_prefix='/api/status')
    app.register_blueprint(key_bp, url_prefix='/api/chaves')
    app.register_blueprint(provider_bp, url_prefix='/api/providers')
    app.register_blueprint(client_bp, url_prefix='/api/clientes')
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
    app.register_blueprint(agent_bp, url_prefix='/api/agentes')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    return app