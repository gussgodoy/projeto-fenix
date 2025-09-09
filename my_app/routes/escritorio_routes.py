# /my_app/routes/escritorio_routes.py

from flask import Blueprint, request, jsonify
from ..db import get_db_connection

escritorio_bp = Blueprint('escritorio', __name__, url_prefix='/api/escritorio')

# --- ROTA DE CONFIGURAÇÃO ---
@escritorio_bp.route('/config', methods=['GET'])
def get_escritorio_config():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Captadores e Indicadores são clientes com status "Ativo" (id=1)
            cur.execute("SELECT id, nome FROM clientes WHERE status_id = 1 ORDER BY nome")
            clientes_ativos = cur.fetchall()
            
            # Statuses
            cur.execute("SELECT id, name, color FROM statuses ORDER BY id")
            statuses = cur.fetchall()
            
            return jsonify({
                "clientes_ativos": clientes_ativos,
                "statuses": statuses
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DE CLIENTES (CRUD) ---

@escritorio_bp.route('/clientes', methods=['GET'])
def get_clientes():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
                SELECT c.*, s.name as status_nome, s.color as status_cor
                FROM clientes c
                LEFT JOIN statuses s ON c.status_id = s.id
                ORDER BY c.nome
            """
            cur.execute(sql)
            clientes = cur.fetchall()
            return jsonify(clientes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.get_json()
    if not data or not data.get('nome'):
        return jsonify({"error": "O nome do cliente é obrigatório"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Prepara os campos e valores para a inserção
            fields = [key for key in data if key != 'id']
            placeholders = ', '.join(['%s'] * len(fields))
            values = [data.get(field) or None for field in fields]

            sql = f"INSERT INTO clientes ({', '.join(fields)}) VALUES ({placeholders})"
            
            cur.execute(sql, tuple(values))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            fields = [key for key in data if key != 'id']
            set_clauses = [f"{field} = %s" for field in fields]
            values = [data.get(field) or None for field in fields]
            values.append(cliente_id)

            sql = f"UPDATE clientes SET {', '.join(set_clauses)} WHERE id = %s"
            
            cur.execute(sql, tuple(values))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Cliente não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Cliente não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()