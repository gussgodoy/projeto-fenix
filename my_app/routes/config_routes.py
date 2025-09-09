import secrets
import json
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# --- ROTAS DE STATUS ---
@config_bp.route('/statuses', methods=['GET', 'POST'])
def handle_statuses():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute("SELECT id, name, color FROM statuses ORDER BY id")
            return jsonify(cursor.fetchall())
        elif request.method == 'POST':
            data = request.get_json()
            name, color = data.get('name'), data.get('color')
            if not all([name, color]):
                return jsonify({"error": "Nome e cor são obrigatórios"}), 400
            cursor.execute("INSERT INTO statuses (name, color) VALUES (%s, %s)", (name, color))
            conn.commit()
            return jsonify({"status": "success", "id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@config_bp.route('/statuses/<int:status_id>', methods=['DELETE', 'PATCH'])
def handle_status_by_id(status_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'DELETE':
            cursor.execute("DELETE FROM statuses WHERE id = %s", (status_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cursor.rowcount > 0 else (jsonify({"error": "Status não encontrado"}), 404)
        elif request.method == 'PATCH':
            data = request.get_json()
            name, color = data.get('name'), data.get('color')
            if not all([name, color]):
                return jsonify({"error": "Nome e cor são obrigatórios"}), 400
            cursor.execute("UPDATE statuses SET name = %s, color = %s WHERE id = %s", (name, color, status_id))
            conn.commit()
            return jsonify({"status": "success"}) if cursor.rowcount > 0 else (jsonify({"error": "Status não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- FUNÇÃO GENÉRICA DE UPDATE DE STATUS ---
def update_record_status(table_name, record_id, status_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if table_name not in ['our_api_keys', 'ia_providers', 'ia_api_keys']:
                return jsonify({"error": "Tabela inválida"}), 400
            sql = f"UPDATE {table_name} SET status_id = %s WHERE id = %s"
            cur.execute(sql, (status_id, record_id))
            conn.commit()
            if cur.rowcount > 0:
                return jsonify({"status": "success", "id": record_id})
            else:
                return jsonify({"error": "Registro não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS "NOSSAS CHAVES API" ---
@config_bp.route('/our-keys', methods=['GET', 'POST'])
def handle_our_keys():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'GET':
            sql = "SELECT k.id, k.service_name, k.api_key, k.status_id, s.name as status_name, s.color as status_color FROM our_api_keys k JOIN statuses s ON k.status_id = s.id ORDER BY k.service_name"
            cursor.execute(sql)
            keys = cursor.fetchall()
            for key in keys: key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(keys)
        elif request.method == 'POST':
            service_name = request.get_json().get('service_name')
            api_key = f"fenix_{secrets.token_urlsafe(32)}"
            cursor.execute("INSERT INTO our_api_keys (service_name, api_key) VALUES (%s, %s)", (service_name, api_key))
            conn.commit()
            return jsonify({"status": "success", "id": cursor.lastrowid, "api_key": api_key}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@config_bp.route('/our-keys/<int:key_id>/status', methods=['PATCH'])
def update_our_key_status_route(key_id):
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DE IA ---
@config_bp.route('/ia/providers', methods=['GET', 'POST'])
def handle_ia_providers():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute("SELECT p.id, p.name, p.status_id, s.name as status_name, s.color as status_color FROM ia_providers p JOIN statuses s ON p.status_id = s.id ORDER BY p.name")
            providers = cursor.fetchall()
            cursor.execute("SELECT k.id, k.provider_id, k.key_name, k.api_key, k.status_id, s.name as status_name, s.color as status_color FROM ia_api_keys k JOIN statuses s ON k.status_id = s.id ORDER BY k.key_name")
            all_keys = cursor.fetchall()
            for provider in providers:
                provider['keys'] = [key for key in all_keys if key['provider_id'] == provider['id']]
                for key in provider['keys']:
                    key['api_key'] = f"****{key['api_key'][-4:]}"
            return jsonify(providers)
        elif request.method == 'POST':
            name = request.get_json().get('name')
            cursor.execute("INSERT INTO ia_providers (name) VALUES (%s)", (name,))
            conn.commit()
            return jsonify({"status": "success", "id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@config_bp.route('/ia/providers/<int:provider_id>/status', methods=['PATCH'])
def update_provider_status_route(provider_id):
    status_id = request.get_json().get('status_id')
    return update_record_status('ia_providers', provider_id, status_id)

@config_bp.route('/ia/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM ia_api_keys WHERE provider_id = %s", (provider_id,))
            cur.execute("DELETE FROM ia_providers WHERE id = %s", (provider_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Provedor não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@config_bp.route('/ia/keys', methods=['POST'])
def create_ia_key():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.get_json()
            provider_id, key_name, api_key = data.get('provider_id'), data.get('key_name'), data.get('api_key')
            cur.execute("INSERT INTO ia_api_keys (provider_id, key_name, api_key) VALUES (%s, %s, %s)", (provider_id, key_name, api_key))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()


@config_bp.route('/ia/keys/<int:key_id>/status', methods=['PATCH'])
def update_ia_key_status_route(key_id):
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS PARA PERFIS DE AGENTES ---

@config_bp.route('/perfis', methods=['GET'])
def get_perfis():
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, nome, config_avancada FROM perfis ORDER BY nome ASC")
            perfis = cur.fetchall()
            for perfil in perfis:
                if isinstance(perfil.get('config_avancada'), str):
                    try:
                        perfil['config_avancada'] = json.loads(perfil['config_avancada'])
                    except (json.JSONDecodeError, TypeError):
                        pass
            return jsonify(perfis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@config_bp.route('/perfis', methods=['POST'])
def create_perfil():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.get_json()
            nome = data.get('nome')
            config = data.get('config_avancada')
            if not nome:
                return jsonify({"error": "O nome é obrigatório"}), 400
            config_str = json.dumps(config) if config else None
            cur.execute("INSERT INTO perfis (nome, config_avancada) VALUES (%s, %s)", (nome, config_str))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@config_bp.route('/perfis/<int:perfil_id>', methods=['PATCH'])
def update_perfil(perfil_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            data = request.get_json()
            nome = data.get('nome')
            config = data.get('config_avancada')
            if not nome:
                return jsonify({"error": "O nome é obrigatório"}), 400
            config_str = json.dumps(config) if config else None
            cur.execute("UPDATE perfis SET nome = %s, config_avancada = %s WHERE id = %s", (nome, config_str, perfil_id))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Perfil não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@config_bp.route('/perfis/<int:perfil_id>', methods=['DELETE'])
def delete_perfil(perfil_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM perfis WHERE id = %s", (perfil_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Perfil não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# /my_app/routes/config_routes.py

# ... (todo o código existente do config_routes.py fica aqui em cima)

@config_bp.route('/health', methods=['GET'])
def health_check():
    # A lógica pode ser expandida para verificar dependências específicas deste módulo
    return jsonify(status="ok", module="Configurações"), 200