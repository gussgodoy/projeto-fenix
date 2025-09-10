# my_app/routes/client_routes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

client_bp = Blueprint('client', __name__)

@client_bp.route('/', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `clientes`;")
            return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

@client_bp.route('/', methods=['POST'])
def create_cliente():
    data = request.get_json(silent=False)
    if not data or 'nome' not in data:
        return jsonify({"error": "O campo 'nome' é obrigatório."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            fields = ', '.join([f"`{k}`" for k in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO clientes ({fields}) VALUES ({placeholders});"
            cursor.execute(sql, list(data.values()))
            new_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": new_id, "message": "Cliente criado com sucesso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao criar cliente: {e}"}), 500
    finally:
        conn.close()

@client_bp.route('/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    data = request.get_json(silent=False)
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            fields_to_update = [f"`{k}` = %s" for k in data.keys()]
            sql = f"UPDATE clientes SET {', '.join(fields_to_update)} WHERE id = %s;"
            values = list(data.values()) + [cliente_id]
            affected_rows = cursor.execute(sql, values)
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Cliente atualizado"}), 200
        else:
            return jsonify({"error": "Cliente não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao atualizar cliente: {e}"}), 500
    finally:
        conn.close()

@client_bp.route('/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            affected_rows = cursor.execute("UPDATE clientes SET status_id = 99 WHERE id = %s;", (cliente_id,))
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Cliente excluído (soft delete)"}), 200
        else:
            return jsonify({"error": "Cliente não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao excluir cliente: {e}"}), 500
    finally:
        conn.close()