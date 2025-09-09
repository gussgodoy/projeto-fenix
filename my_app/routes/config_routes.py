import secrets
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# --- (As rotas de Status e Nossas Chaves permanecem as mesmas) ---
@config_bp.route('/statuses', methods=['GET'])
def get_statuses():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, color FROM statuses ORDER BY id")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@config_bp.route('/statuses', methods=['POST'])
def create_status():
    data = request.get_json()
    name, color = data.get('name'), data.get('color')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO statuses (name, color) VALUES (%s, %s)", (name, color))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        conn.close()

@config_bp.route('/statuses/<int:status_id>', methods=['DELETE'])
def delete_status(status_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM statuses WHERE id = %s", (status_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Status não encontrado"}), 404)
    finally:
        conn.close()

def update_record_status(table_name, record_id, status_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if table_name not in ['our_api_keys', 'ia_providers', 'ia_api_keys']:
                return jsonify({"error": "Tabela inválida"}), 400
            
            sql = f"UPDATE {table_name} SET status_id = %s WHERE id = %s"
            cur.execute(sql, (status_id, record_id))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Registro não encontrado"}), 404)
    finally:
        conn.close()

@config_bp.route('/our-keys', methods=['GET'])
def get_our_keys():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = "SELECT k.id, k.service_name, k.api_key, s.name as status_name, s.color as status_color FROM our_api_keys k JOIN statuses s ON k.status_id = s.id ORDER BY k.service_name"
            cur.execute(sql)
            keys = cur.fetchall()
            for key in keys: key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
    finally:
        conn.close()

@config_bp.route('/our-keys', methods=['POST'])
def create_our_key():
    service_name = request.get_json().get('service_name')
    api_key = f"fenix_{secrets.token_urlsafe(32)}"
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO our_api_keys (service_name, api_key) VALUES (%s, %s)", (service_name, api_key))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid, "api_key": api_key}), 201
    finally:
        conn.close()

@config_bp.route('/our-keys/<int:key_id>/status', methods=['PATCH'])
def update_our_key_status(key_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('our_api_keys', key_id, status_id)

@config_bp.route('/our-keys/<int:key_id>', methods=['DELETE'])
def delete_our_key(key_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM our_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Chave não encontrada"}), 404)
    finally:
        conn.close()

@config_bp.route('/ia/providers', methods=['GET'])
def get_providers_and_keys():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT p.id, p.name, s.name as status_name, s.color as status_color FROM ia_providers p JOIN statuses s ON p.status_id = s.id ORDER BY p.name")
            providers = cur.fetchall()
            cur.execute("SELECT k.id, k.provider_id, k.key_name, k.api_key, s.name as status_name, s.color as status_color FROM ia_api_keys k JOIN statuses s ON k.status_id = s.id ORDER BY k.key_name")
            all_keys = cur.fetchall()
            for provider in providers:
                provider['keys'] = [key for key in all_keys if key['provider_id'] == provider['id']]
                for key in provider['keys']:
                    key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(providers)
    finally:
        conn.close()

@config_bp.route('/ia/providers', methods=['POST'])
def create_provider():
    name = request.get_json().get('name')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ia_providers (name) VALUES (%s)", (name,))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        conn.close()

@config_bp.route('/ia/providers/<int:provider_id>/status', methods=['PATCH'])
def update_provider_status(provider_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('ia_providers', provider_id, status_id)
    
@config_bp.route('/ia/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_providers WHERE id = %s", (provider_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Provedor não encontrado"}), 404)
    finally:
        conn.close()

@config_bp.route('/ia/keys', methods=['POST'])
def create_ia_key():
    data = request.get_json()
    provider_id, key_name, api_key = data.get('provider_id'), data.get('key_name'), data.get('api_key')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ia_api_keys (provider_id, key_name, api_key) VALUES (%s, %s, %s)", (provider_id, key_name, api_key))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        conn.close()

@config_bp.route('/ia/keys/<int:key_id>/status', methods=['PATCH'])
def update_ia_key_status(key_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('ia_api_keys', key_id, status_id)

@config_bp.route('/ia/keys/<int:key_id>', methods=['DELETE'])
def delete_ia_key(key_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_api_keys WHERE id = %s", (key_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Chave não encontrada"}), 404)
    finally:
        conn.close()