# my_app/routes/agent_routes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection
import urllib.parse
import google.generativeai as genai

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/', methods=['GET'])
def get_all_agentes():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT a.*, c.nome AS cliente_nome, p.nome AS perfil_nome
            FROM agentes a
            LEFT JOIN clientes c ON a.cliente_id = c.id
            LEFT JOIN perfis p ON a.perfil_id = p.id
            WHERE a.status_id = 1;
            """
            cursor.execute(sql)
            return jsonify(cursor.fetchall()), 200
    finally:
        if conn: conn.close()

@agent_bp.route('/<int:agent_id>', methods=['GET'])
def get_agente_por_id(agent_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT a.*, c.nome AS cliente_nome, p.nome AS perfil_nome
            FROM agentes a
            LEFT JOIN clientes c ON a.cliente_id = c.id
            LEFT JOIN perfis p ON a.perfil_id = p.id
            WHERE a.id = %s;
            """
            cursor.execute(sql, (agent_id,))
            data = cursor.fetchone()
            return jsonify(data) if data else (jsonify({"error": "Agente não encontrado"}), 404)
    finally:
        if conn: conn.close()

@agent_bp.route('/', methods=['POST'])
def create_agente():
    data = request.get_json()
    nome = data.get('nome')
    if not nome:
        return jsonify({"error": "O campo 'nome' é obrigatório"}), 400

    iniciais = "".join([n[0] for n in nome.split() if n])[:2].upper()
    avatar_url = f"https://ui-avatars.com/api/?name={urllib.parse.quote(iniciais)}&background=FF6D00&color=FFFFFF&bold=true"

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO agentes (nome, avatar_url) VALUES (%s, %s);"
            cursor.execute(sql, (nome, avatar_url))
            new_id = cursor.lastrowid
        conn.commit()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM agentes WHERE id = %s;", (new_id,))
            new_agente = cursor.fetchone()
        return jsonify(new_agente), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao criar agente: {e}"}), 500
    finally:
        conn.close()

@agent_bp.route('/<int:agent_id>', methods=['PUT'])
def update_agente(agent_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    fields_to_update = [f"`{k}` = %s" for k in data.keys()]
    values = list(data.values())

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            values.append(agent_id)
            sql = f"UPDATE agentes SET {', '.join(fields_to_update)} WHERE id = %s;"
            cursor.execute(sql, values)
        conn.commit()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM agentes WHERE id = %s;", (agent_id,))
            updated_agente = cursor.fetchone()
        return jsonify(updated_agente), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao atualizar agente: {e}"}), 500
    finally:
        conn.close()

@agent_bp.route('/<int:agent_id>', methods=['DELETE'])
def delete_agente(agent_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE conexoes SET agente_id = NULL WHERE agente_id = %s;", (agent_id,))
            affected_rows = cursor.execute("UPDATE agentes SET status_id = 99 WHERE id = %s;", (agent_id,))
        conn.commit()
        if affected_rows > 0:
            return jsonify({"message": "Agente excluído (soft delete)"}), 200
        else:
            return jsonify({"error": "Agente não encontrado"}), 404
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao excluir agente: {e}"}), 500
    finally:
        conn.close()

@agent_bp.route('/chat', methods=['POST'])
def handle_chat():
    data = request.get_json()
    agent_id = data.get('agent_id')
    user_message = data.get('message')
    conversation_id = data.get('conversation_id')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM agentes WHERE id = %s;", (agent_id,))
            agente = cursor.fetchone()
            if not agente or agente.get('status_id') != 1 or agente.get('bloqueio_cliente') == 1:
                return jsonify({"response": "Agente indisponível."}), 200

            if conversation_id:
                cursor.execute("SELECT conversa_bloqueada FROM conversations WHERE id = %s;", (conversation_id,))
                conversa = cursor.fetchone()
                if conversa and conversa.get('conversa_bloqueada') == 1:
                    return jsonify({"response": ""}), 200

            cursor.execute("SELECT valor FROM chaves WHERE id = %s;", (agente.get('chave_id'),))
            chave_api_obj = cursor.fetchone()
            if not chave_api_obj: return jsonify({"error": "Chave de API não encontrada."}), 400
            
            GOOGLE_API_KEY = chave_api_obj['valor']
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # (Lógica do Gemini e Geração de Resposta aqui...)
            # Esta parte pode ser complexa e foi simplificada.
            # Adapte conforme a lógica completa do seu arquivo original.
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(user_message)
            ai_message = response.text or ""

        return jsonify({"response": ai_message}), 200
    except Exception as e:
        return jsonify({"error": f"Erro no chat: {e}"}), 500
    finally:
        if conn: conn.close()