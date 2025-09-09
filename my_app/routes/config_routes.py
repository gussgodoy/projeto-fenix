import secrets
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# --- ROTAS PARA "NOSSAS CHAVES API" ---
# (Esta secção permanece igual)
def generate_api_key():
    return f"fenix_{secrets.token_urlsafe(32)}"

@config_bp.route('/our-keys', methods=['GET'])
def get_our_keys():
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
    service_name = request.get_json().get('service_name')
    if not service_name:
        return jsonify({"error": "O nome do serviço (service_name) é obrigatório"}), 400
    api_key = generate_api_key()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO our_api_keys (service_name, api_key) VALUES (%s, %s)", (service_name, api_key))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid, "api_key": api_key}), 201
    finally:
        conn.close()

@config_bp.route('/our-keys/<int:key_id>', methods=['DELETE'])
def delete_our_key(key_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM our_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            if cur.rowcount == 0: return jsonify({"error": "Chave não encontrada"}), 404
            return jsonify({"status": "success"})
    finally:
        conn.close()

# --- ROTAS PARA PROVEDORES DE IA (AGORA COM GESTÃO COMPLETA) ---

@config_bp.route('/ia/providers', methods=['GET'])
def get_providers():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ia_providers ORDER BY name")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@config_bp.route('/ia/providers', methods=['POST'])
def create_provider():
    """NOVO: Adiciona um novo provedor de IA."""
    name = request.get_json().get('name')
    if not name:
        return jsonify({"error": "O nome (name) do provedor é obrigatório"}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ia_providers (name) VALUES (%s)", (name,))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao criar provedor: {e}"}), 500
    finally:
        conn.close()

@config_bp.route('/ia/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """NOVO: Deleta um provedor de IA (e as suas chaves associadas, por causa do 'ON DELETE CASCADE')."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_providers WHERE id = %s", (provider_id,))
            conn.commit()
            if cur.rowcount == 0: return jsonify({"error": "Provedor não encontrado"}), 404
            return jsonify({"status": "success"})
    finally:
        conn.close()

# --- ROTAS PARA CHAVES DE API DE IA (AGORA COM FILTRO) ---

@config_bp.route('/ia/providers/<int:provider_id>/keys', methods=['GET'])
def get_keys_for_provider(provider_id):
    """NOVO: Retorna todas as chaves de API para um provedor específico."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT id, key_name, api_key FROM ia_api_keys WHERE provider_id = %s ORDER BY key_name"
            cur.execute(sql, (provider_id,))
            keys = cur.fetchall()
            for key in keys:
                key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
    finally:
        conn.close()

@config_bp.route('/ia/keys', methods=['POST'])
def create_ia_key():
    data = request.get_json()
    provider_id, key_name, api_key = data.get('provider_id'), data.get('key_name'), data.get('api_key')
    if not all([provider_id, key_name, api_key]):
        return jsonify({"error": "provider_id, key_name, e api_key são obrigatórios"}), 400
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ia_api_keys (provider_id, key_name, api_key) VALUES (%s, %s, %s)",(provider_id, key_name, api_key))
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