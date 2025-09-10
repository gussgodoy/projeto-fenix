# my_app/routes/provider_routes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

provider_bp = Blueprint('provider', __name__)

@provider_bp.route('/', methods=['GET'])
def get_provedores():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, status, descricao FROM provedores WHERE status_id = 1 ORDER BY id DESC;")
            rows = cursor.fetchall()
            return jsonify(rows), 200
    finally:
        if conn: conn.close()

@provider_bp.route('/', methods=['POST'])
def create_provedor():
    data = request.get_json(silent=False)
    if not data or not data.get('nome'):
        return jsonify({"error": "O nome do provedor é obrigatório."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO provedores (nome, status, descricao) VALUES (%s, %s, %s);"
            cursor.execute(sql, (data.get('nome'), data.get('status'), data.get('descricao')))
            new_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": new_id, "message": "Provedor criado com sucesso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao criar provedor: {e}"}), 500
    finally:
        conn.close()

@provider_bp.route('/<int:provedor_id>', methods=['PUT'])
def update_provedor(provedor_id):
    data = request.get_json(silent=False)
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            fields_to_update = [f"`{k}` = %s" for k in data.keys()]
            sql = f"UPDATE provedores SET {', '.join(fields_to_update)} WHERE id = %s;"
            values = list(data.values()) + [provedor_id]
            affected_rows = cursor.execute(sql, values)
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Provedor atualizado"}), 200
        else:
            return jsonify({"error": "Provedor não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao atualizar provedor: {e}"}), 500
    finally:
        conn.close()

@provider_bp.route('/<int:provedor_id>', methods=['DELETE'])
def delete_provedor(provedor_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE chaves SET status_id = 99 WHERE provedor_id = %s;", (provedor_id,))
            affected_rows = cursor.execute("UPDATE provedores SET status_id = 99 WHERE id = %s;", (provedor_id,))
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Provedor e chaves associadas excluídos (soft delete)"}), 200
        else:
            return jsonify({"error": "Provedor não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao excluir provedor: {e}"}), 500
    finally:
        conn.close()