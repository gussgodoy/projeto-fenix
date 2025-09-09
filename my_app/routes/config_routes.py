import secrets
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# --- CRUD PARA A TABELA DE STATUS ---

@config_bp.route('/statuses', methods=['GET'])
def get_statuses():
    """Retorna todos os status disponíveis."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, color FROM statuses ORDER BY id")
            return jsonify(cur.fetchall())
    finally:
        conn.close()

@config_bp.route('/statuses', methods=['POST'])
def create_status():
    """Cria um novo status."""
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
    """Deleta um status."""
    # Adicionar lógica para verificar se o status não está em uso antes de deletar seria ideal em produção.
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM statuses WHERE id = %s", (status_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Status não encontrado"}), 404)
    finally:
        conn.close()

# --- FUNÇÃO GENÉRICA PARA ATUALIZAR STATUS ---
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

# --- ROTAS PARA "NOSSAS CHAVES API" ---
@config_bp.route('/our-keys', methods=['GET'])
def get_our_keys():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT k.id, k.service_name, k.api_key, s.name as status_name, s.color as status_color
                FROM our_api_keys k
                JOIN statuses s ON k.status_id = s.id
                ORDER BY k.service_name
            """
            cur.execute(sql)
            keys = cur.fetchall()
            for key in keys:
                key['api_key'] = f"****{key['api_key'][-4:]}"
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
    # Lógica de delete existente
    pass # O código anterior para delete continua válido

# --- ROTAS PARA PROVEDORES DE IA E SUAS CHAVES (LÓGICA ANINHADA) ---
@config_bp.route('/ia/providers', methods=['GET'])
def get_providers_and_keys():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Esta query busca os provedores e aninha as suas chaves como um objeto JSON
            sql = """
                SELECT 
                    p.id, p.name, 
                    s_p.name as status_name, s_p.color as status_color,
                    (SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'id', k.id, 
                            'key_name', k.key_name, 
                            'api_key', CONCAT('****', RIGHT(k.api_key, 4)), 
                            'status_name', s_k.name,
                            'status_color', s_k.color
                        ))
                     FROM ia_api_keys k 
                     JOIN statuses s_k ON k.status_id = s_k.id
                     WHERE k.provider_id = p.id
                    ) as keys
                FROM ia_providers p
                JOIN statuses s_p ON p.status_id = s_p.id
                ORDER BY p.name;
            """
            cur.execute(sql)
            providers = cur.fetchall()
            for provider in providers:
                if provider['keys'] is None:
                    provider['keys'] = []
            return jsonify(providers)
    finally:
        conn.close()

@config_bp.route('/ia/providers', methods=['POST'])
def create_provider():
    # Lógica de criar provedor existente
    pass # O código anterior continua válido

@config_bp.route('/ia/providers/<int:provider_id>/status', methods=['PATCH'])
def update_provider_status(provider_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('ia_providers', provider_id, status_id)
    
@config_bp.route('/ia/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    # Lógica de delete de provedor existente
    pass # O código anterior continua válido

# --- ROTAS PARA CHAVES DE IA (CRIAR, DELETAR, ATUALIZAR STATUS) ---
@config_bp.route('/ia/keys', methods=['POST'])
def create_ia_key():
    # Lógica de criar chave de IA existente
    pass # O código anterior continua válido

@config_bp.route('/ia/keys/<int:key_id>/status', methods=['PATCH'])
def update_ia_key_status(key_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('ia_api_keys', key_id, status_id)

@config_bp.route('/ia/keys/<int:key_id>', methods=['DELETE'])
def delete_ia_key(key_id):
    # Lógica de delete de chave de IA existente
    pass # O código anterior para delete continua válido