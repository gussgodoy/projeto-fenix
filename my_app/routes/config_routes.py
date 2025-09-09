import secrets
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# --- ROTAS PARA "NOSSAS CHAVES API" ---

def generate_api_key():
    """Gera uma chave de API segura."""
    return f"fenix_{secrets.token_urlsafe(32)}"

@config_bp.route('/our-keys', methods=['GET'])
def get_our_keys():
    """Retorna todas as nossas chaves de API."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, service_name, api_key, is_active, created_at FROM our_api_keys ORDER BY created_at DESC")
            keys = cur.fetchall()
            for key in keys:
                key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
    finally:
        conn.close()

@config_bp.route('/our-keys', methods=['POST'])
def create_our_key():
    """Cria uma nova chave de API para o nosso sistema."""
    data = request.get_json()
    service_name = data.get('service_name')
    if not service_name:
        return jsonify({"error": "O nome do serviço (service_name) é obrigatório"}), 400

    api_key = generate_api_key()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO our_api_keys (service_name, api_key) VALUES (%s, %s)",
                (service_name, api_key)
            )
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid, "api_key": api_key}), 201
    finally:
        conn.close()

@config_bp.route('/our-keys/<int:key_id>', methods=['DELETE'])
def delete_our_key(key_id):
    """Deleta uma das nossas chaves de API."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM our_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            if cur.rowcount == 0: return jsonify({"error": "Chave não encontrada"}), 404
            return jsonify({"status": "success"})
    finally:
        conn.close()


# --- ROTAS PARA PROVEDORES DE IA ---

@config_bp.route('/ia/providers', methods=['GET'])
def get_providers():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ia_providers ORDER BY name")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

# --- ROTAS PARA CHAVES DE API DE IA ---

@config_bp.route('/ia/keys', methods=['GET'])
def get_ia_keys():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT k.id, k.key_name, k.api_key, p.name as provider_name
                FROM ia_api_keys k JOIN ia_providers p ON k.provider_id = p.id
                ORDER BY p.name, k.key_name
            """
            cur.execute(sql)
            keys = cur.fetchall()
            for key in keys:
                key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
    finally:
        conn.close()

@config_bp.route('/ia/keys', methods=['POST'])
def create_ia_key():
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

@config_bp.route('/ia/keys/<int:key_id>', methods=['DELETE'])
def delete_ia_key(key_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            if cur.rowcount == 0: return jsonify({"error": "Chave não encontrada"}), 404
            return jsonify({"status": "success"})
    finally:
        conn.close()