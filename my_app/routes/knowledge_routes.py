# /my_app/routes/knowledge_routes.py

from flask import Blueprint, request, jsonify
from ..db import get_db_connection

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

# --- ROTA DE CONFIGURAÇÃO ---
@knowledge_bp.route('/config', methods=['GET'])
def get_knowledge_config():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome FROM clientes WHERE status_id = 1 ORDER BY nome")
            clientes = cur.fetchall()
            return jsonify({"clientes": clientes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DE TEMPLATES (CRUD) ---

@knowledge_bp.route('/templates', methods=['GET'])
def get_templates():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
                SELECT t.id, t.name, t.cliente_id, c.nome as cliente_nome
                FROM knowledge_templates t
                LEFT JOIN clientes c ON t.cliente_id = c.id
                ORDER BY t.name
            """
            cur.execute(sql)
            templates = cur.fetchall()
            return jsonify(templates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/templates', methods=['POST'])
def create_template():
    data = request.get_json()
    name = data.get('name')
    cliente_id = data.get('cliente_id') or None
    if not name:
        return jsonify({"error": "O nome do template é obrigatório"}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO knowledge_templates (name, cliente_id) VALUES (%s, %s)",
                (name, cliente_id)
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.execute("SELECT t.id, t.name, t.cliente_id, c.nome as cliente_nome FROM knowledge_templates t LEFT JOIN clientes c ON t.cliente_id = c.id WHERE t.id = %s", (new_id,))
            new_template = cur.fetchone()
            return jsonify(new_template), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM knowledge_cards WHERE template_id = %s", (template_id,))
            cur.execute("DELETE FROM knowledge_templates WHERE id = %s", (template_id,))
            conn.commit()
            return jsonify(status="success"), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DE CARDS (CRUD) ---

@knowledge_bp.route('/templates/<int:template_id>/cards', methods=['GET'])
def get_cards_for_template(template_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM knowledge_cards WHERE template_id = %s ORDER BY title", (template_id,))
            cards = cur.fetchall()
            return jsonify(cards)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    template_id = data.get('template_id')
    if not all([title, content, template_id]):
        return jsonify({"error": "Título, conteúdo e ID do template são obrigatórios"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO knowledge_cards (template_id, title, content) VALUES (%s, %s, %s)",
                (template_id, title, content)
            )
            conn.commit()
            return jsonify(status="success", id=cur.lastrowid), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    if not all([title, content]):
        return jsonify({"error": "Título e conteúdo são obrigatórios"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE knowledge_cards SET title = %s, content = %s WHERE id = %s",
                (title, content, card_id)
            )
            conn.commit()
            return jsonify(status="success") if cur.rowcount > 0 else (jsonify({"error": "Card não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM knowledge_cards WHERE id = %s", (card_id,))
            conn.commit()
            return jsonify(status="success"), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# Rota de Saúde para o Módulo
@knowledge_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok", module="Conhecimento"), 200