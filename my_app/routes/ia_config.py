from flask import Blueprint, request, jsonify
from ..db import get_db_connection

# Cria um "Blueprint", um conjunto de rotas que pode ser registrado na aplicação principal
ia_bp = Blueprint('ia_config', __name__, url_prefix='/api/ia')

# --- ROTAS PARA PROVEDORES ---

@ia_bp.route('/providers', methods=['GET'])
def get_providers():
    """Retorna todos os provedores de IA."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ia_providers ORDER BY name")
            providers = cur.fetchall()
            return jsonify(providers)
    finally:
        conn.close()

# --- ROTAS PARA CHAVES DE API ---

@ia_bp.route('/keys', methods=['GET'])
def get_all_keys():
    """Retorna todas as chaves de API, juntando o nome do provedor."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    k.id, k.key_name, k.api_key, k.is_active,
                    p.name as provider_name
                FROM ia_api_keys k
                JOIN ia_providers p ON k.provider_id = p.id
                ORDER BY p.name, k.key_name
            """
            cur.execute(sql)
            keys = cur.fetchall()
            # Esconde a chave de API por segurança, mostrando apenas os últimos 4 caracteres
            for key in keys:
                key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
    finally:
        conn.close()

@ia_bp.route('/keys', methods=['POST'])
def create_key():
    """Cria uma nova chave de API."""
    data = request.get_json()
    provider_id = data.get('provider_id')
    key_name = data.get('key_name')
    api_key = data.get('api_key')

    if not all([provider_id, key_name, api_key]):
        return jsonify({"error": "provider_id, key_name, e api_key são obrigatórios"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ia_api_keys (provider_id, key_name, api_key) VALUES (%s, %s, %s)",
                (provider_id, key_name, api_key)
            )
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        conn.close()

@ia_bp.route('/keys/<int:key_id>', methods=['DELETE'])
def delete_key(key_id):
    """Deleta uma chave de API."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            if cur.rowcount == 0:
                return jsonify({"error": "Chave não encontrada"}), 404
            return jsonify({"status": "success"})
    finally:
        conn.close()