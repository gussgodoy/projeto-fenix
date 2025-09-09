# /projeto-fenix/my_app/routes/dashboard.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

# Todas as rotas definidas aqui terão o prefixo '/api/dashboard'
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/conversations', methods=['GET'])
def get_dashboard_conversations():
    cliente_id = request.args.get('cliente_id')
    if not cliente_id:
        return jsonify({"error": "cliente_id é obrigatório"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # --- CORREÇÃO DEFINITIVA: 'c.timestamp' alterado para 'c.data_inicio' ---
            sql = """
            SELECT
                c.id, c.conversa_bloqueada, ct.nome as customer_name,
                (SELECT conteudo FROM messages WHERE conversation_id = c.id ORDER BY timestamp DESC LIMIT 1) as last_message_snippet
            FROM conversations c
            INNER JOIN agentes a ON c.agente_id = a.id
            LEFT JOIN contacts ct ON c.contact_id = ct.id
            WHERE a.cliente_id = %s
            ORDER BY c.data_inicio DESC;
            """
            cursor.execute(sql, (cliente_id,))
            conversations = cursor.fetchall()
        return jsonify(conversations), 200
    except Exception as e:
        return jsonify({"error": f"Erro fatal na query de conversas: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/messages', methods=['GET'])
def get_dashboard_messages(convo_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM conversations WHERE id = %s", (convo_id,))
            if not cursor.fetchone():
                return jsonify([]), 200
            sql = "SELECT * FROM messages WHERE conversation_id = %s ORDER BY timestamp ASC;"
            cursor.execute(sql, (convo_id,))
            messages = cursor.fetchall()
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": f"Erro fatal na query de mensagens: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/toggle-lock', methods=['PUT'])
def toggle_conversation_lock(convo_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM conversations WHERE id = %s", (convo_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Conversa não encontrada"}), 404
            sql_update = "UPDATE conversations SET conversa_bloqueada = NOT conversa_bloqueada WHERE id = %s;"
            cursor.execute(sql_update, (convo_id,))
        conn.commit()
        with conn.cursor() as cursor:
            sql_select = "SELECT c.id, c.conversa_bloqueada, ct.nome as customer_name FROM conversations c LEFT JOIN contacts ct ON c.contact_id = ct.id WHERE c.id = %s;"
            cursor.execute(sql_select, (convo_id,))
            updated_conversation = cursor.fetchone()
        return jsonify(updated_conversation), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao alternar bloqueio: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@dashboard_bp.route('/conversations/<int:convo_id>/send-message', methods=['POST'])
def send_human_message(convo_id):
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "O conteúdo da mensagem é obrigatório"}), 400
    message_content = data['content']
    human_user_id = 1
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM conversations WHERE id = %s", (convo_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Conversa não encontrada"}), 404
            sql = "INSERT INTO messages (conversation_id, conteudo, sender_type, user_id) VALUES (%s, %s, 'human', %s);"
            cursor.execute(sql, (convo_id, message_content, human_user_id))
            new_message_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": new_message_id, "message": "Mensagem enviada com sucesso"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao enviar mensagem: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# /my_app/routes/dashboard.py

from flask import Blueprint, jsonify

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok", module="Dashboard"), 200

# ... (o resto do seu código para este módulo continua aqui)        