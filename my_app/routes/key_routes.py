# my_app/routes/key_routes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

key_bp = Blueprint('key', __name__)

@key_bp.route('/', methods=['GET'])
def get_chaves():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `chaves` WHERE status_id = 1;")
            return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()


@key_bp.route('/', methods=['POST'])
def create_chave():
    data = request.get_json(silent=False)
    if not data or not data.get('apelido') or not data.get('valor') or not data.get('provedor_id'):
        return jsonify({"error": "Campos 'apelido', 'valor' e 'provedor_id' são obrigatórios."}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO chaves (apelido, valor, status, provedor_id) VALUES (%s, %s, %s, %s);"
            cursor.execute(sql, (data.get('apelido'), data.get('valor'), data.get('status', 'ativo'), data.get('provedor_id')))
            new_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": new_id, "message": "Chave criada com sucesso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao criar chave: {e}"}), 500
    finally:
        conn.close()

@key_bp.route('/<int:chave_id>', methods=['PUT'])
def update_chave(chave_id):
    data = request.get_json(silent=False)
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            fields_to_update = [f"`{k}` = %s" for k in data.keys()]
            sql = f"UPDATE chaves SET {', '.join(fields_to_update)} WHERE id = %s;"
            values = list(data.values()) + [chave_id]
            affected_rows = cursor.execute(sql, values)
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Chave atualizada"}), 200
        else:
            return jsonify({"error": "Chave não encontrada"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao atualizar chave: {e}"}), 500
    finally:
        conn.close()

@key_bp.route('/<int:chave_id>', methods=['DELETE'])
def delete_chave(chave_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            affected_rows = cursor.execute("UPDATE chaves SET status_id = 99 WHERE id = %s;", (chave_id,))
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Chave excluída (soft delete)"}), 200
        else:
            return jsonify({"error": "Chave não encontrada"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao excluir chave: {e}"}), 500
    finally:
        conn.close()