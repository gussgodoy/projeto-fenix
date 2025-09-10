# my_app/routes/dashboard.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/conversations', methods=['GET'])
def get_dashboard_conversations():
    cliente_id = request.args.get('cliente_id')
    if not cliente_id:
        return jsonify({"error": "cliente_id é obrigatório"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT c.id, c.conversa_bloqueada, ct.name as customer_name,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_snippet
            FROM conversations c
            INNER JOIN agentes a ON c.agente_id = a.id
            LEFT JOIN contacts ct ON c.contact_id = ct.id
            WHERE a.cliente_id = %s
            ORDER BY c.updated_at DESC;
            """
            cursor.execute(sql, (cliente_id,))
            return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/messages', methods=['GET'])
def get_dashboard_messages(convo_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM messages WHERE conversation_id = %s ORDER BY created_at ASC;"
            cursor.execute(sql, (convo_id,))
            return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/toggle-lock', methods=['PUT'])
def toggle_conversation_lock(convo_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_update = "UPDATE conversations SET conversa_bloqueada = NOT conversa_bloqueada WHERE id = %s;"
            cursor.execute(sql_update, (convo_id,))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao alternar bloqueio: {e}"}), 500
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/send-message', methods=['POST'])
def send_human_message(convo_id):
    data = request.get_json()
    content = data.get('content')
    if not content:
        return jsonify({"error": "O conteúdo da mensagem é obrigatório"}), 400
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO messages (conversation_id, content, sender_type, user_id) VALUES (%s, %s, 'human', 1);"
            cursor.execute(sql, (convo_id, content))
            new_message_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": new_message_id, "message": "Mensagem enviada"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao enviar mensagem: {e}"}), 500
    finally:
        if conn: conn.close()