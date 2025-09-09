# /projeto-fenix/my_app/db.py

import pymysql
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_db_connection():
    """Retorna uma nova conexão com o banco de dados Aiven."""
    
    # O Aiven usa SSL, precisamos do caminho para o certificado.
    # Garanta que o arquivo 'ca.pem' do Aiven está na raiz do seu projeto 'fenix'.
    ssl_ca_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ca.pem')

    if not os.path.exists(ssl_ca_path):
        raise FileNotFoundError("Certificado 'ca.pem' não encontrado na raiz do projeto.")

    db_config = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_NAME"),
        'port': int(os.getenv("DB_PORT", 3306)),
        'cursorclass': pymysql.cursors.DictCursor,
        'charset': 'utf8mb4',
        'ssl': {
            'ca': ssl_ca_path
        }
    }
    return pymysql.connect(**db_config)