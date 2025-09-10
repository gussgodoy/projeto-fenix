# my_app/routes/knowledge_routes.py
from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('/templates', methods=['GET'])
def get_templates():
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            query = """
                SELECT
                    t.id, t.nome, t.descricao, t.cliente_id, c.nome_fantasia AS cliente_nome,
                    (SELECT COUNT(*) FROM knowledge_cards WHERE template_id = t.id AND status_id = 1) AS card_count
                FROM knowledge_templates t
                LEFT JOIN clientes c ON t.cliente_id = c.id
                WHERE t.status_id = 1
                ORDER BY t.nome;
            """
            cur.execute(query)
            templates = cur.fetchall()
            return jsonify(templates)
    finally:
        if conn: conn.close()

@knowledge_bp.route('/cards/<int:template_id>', methods=['GET'])
def get_cards_for_template(template_id):
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, titulo, conteudo FROM knowledge_cards WHERE template_id = %s AND status_id = 1 ORDER BY titulo;", (template_id,))
            cards = cur.fetchall()
            return jsonify(cards)
    finally:
        if conn: conn.close()