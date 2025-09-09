# /my_app/routes/agente_routes.py

from flask import Blueprint, request, jsonify
from ..db import get_db_connection

agente_bp = Blueprint('agente', __name__, url_prefix='/api/agente')

@agente_bp.route('/config', methods=['GET'])
def get_agente_config():
    """ Rota única para carregar todos os dados necessários para os seletores do frontend. """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Status
            cur.execute("SELECT id, name FROM statuses ORDER BY id")
            statuses = cur.fetchall()
            # Clientes
            cur.execute("SELECT id, nome FROM clientes WHERE status_id = 1 ORDER BY nome")
            clientes = cur.fetchall()
            # Provedores
            cur.execute("SELECT id, name FROM ia_providers WHERE status_id = 1 ORDER BY name")
            provedores = cur.fetchall()
            # Chaves
            cur.execute("SELECT id, key_name, provider_id FROM ia_api_keys WHERE status_id = 1 ORDER BY key_name")
            chaves = cur.fetchall()
            # Perfis
            cur.execute("SELECT id, nome, config_avancada FROM perfis ORDER BY nome")
            perfis = cur.fetchall()
            # Templates
            cur.execute("SELECT id, name FROM knowledge_templates ORDER BY name")
            templates = cur.fetchall()

            return jsonify({
                "statuses": statuses,
                "clientes": clientes,
                "provedores": provedores,
                "chaves": chaves,
                "perfis": perfis,
                "templates": templates
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@agente_bp.route('/agentes', methods=['GET'])
def get_agentes():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Seleciona todos os campos do agente
            cur.execute("SELECT * FROM agentes ORDER BY nome")
            agentes = cur.fetchall()
            return jsonify(agentes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@agente_bp.route('/agentes', methods=['POST'])
def create_agente():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({"error": "O nome é obrigatório"}), 400
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO agentes (nome) VALUES (%s)", (nome,))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@agente_bp.route('/agentes/<int:agente_id>', methods=['PUT'])
def update_agente(agente_id):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            fields = [key for key in data if key in [
                'status_id', 'cliente_id', 'chave_id', 'perfil_id', 'template_id',
                'temperature', 'top_p', 'max_tokens'
            ]]
            
            set_clauses = []
            values = []
            for field in fields:
                value = data.get(field)
                set_clauses.append(f"{field} = %s")
                values.append(value if str(value).strip() != '' else None)
            
            if not set_clauses:
                return jsonify({"error": "Nenhum campo para atualizar"}), 400
            
            values.append(agente_id)
            sql = f"UPDATE agentes SET {', '.join(set_clauses)} WHERE id = %s"
            
            cur.execute(sql, tuple(values))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Agente não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@agente_bp.route('/agentes/<int:agente_id>', methods=['DELETE'])
def delete_agente(agente_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agentes WHERE id = %s", (agente_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Agente não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# /my_app/routes/agente_routes.py

from flask import Blueprint, jsonify

agente_bp = Blueprint('agente_bp', __name__, url_prefix='/api/agente')

@agente_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok", module="Agente"), 200

# ... (o resto do seu código para este módulo continua aqui)