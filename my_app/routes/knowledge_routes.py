# my_app/routes/knowledge_routes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection

knowledge_bp = Blueprint('knowledge', __name__)

# Rota para obter todos os templates com contagem de cards
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

# Rota para obter os cards de um template específico
@knowledge_bp.route('/cards/<int:template_id>', methods=['GET'])
def get_cards_for_template(template_id):
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT id, titulo, conteudo FROM knowledge_cards
                WHERE template_id = %s AND status_id = 1 ORDER BY titulo;
            """, (template_id,))
            cards = cur.fetchall()
            return jsonify(cards)
    finally:
        if conn: conn.close()

# Rota para criar um novo template
@knowledge_bp.route('/templates', methods=['POST'])
def create_template():
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO knowledge_templates (nome, descricao, cliente_id) VALUES (%s, %s, %s)",
                (data.get('nome'), data.get('descricao'), data.get('cliente_id'))
            )
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        if conn: conn.close()

# Rota para atualizar um template
@knowledge_bp.route('/templates/<int:id>', methods=['PUT'])
def update_template(id):
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE knowledge_templates SET nome = %s, descricao = %s, cliente_id = %s WHERE id = %s",
                (data.get('nome'), data.get('descricao'), data.get('cliente_id'), id)
            )
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        if conn: conn.close()

# Rota para deletar um template (soft delete)
@knowledge_bp.route('/templates/<int:id>', methods=['DELETE'])
def delete_template(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE knowledge_cards SET status_id = 99 WHERE template_id = %s", (id,))
            cur.execute("UPDATE knowledge_templates SET status_id = 99 WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        if conn: conn.close()

# Rota para criar um card
@knowledge_bp.route('/cards', methods=['POST'])
def create_card():
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO knowledge_cards (template_id, titulo, conteudo) VALUES (%s, %s, %s)",
                (data.get('template_id'), data.get('titulo'), data.get('conteudo'))
            )
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        if conn: conn.close()

# Rota para atualizar um card
@knowledge_bp.route('/cards/<int:id>', methods=['PUT'])
def update_card(id):
    data = request.get_json()
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE knowledge_cards SET titulo = %s, conteudo = %s WHERE id = %s",
                (data.get('titulo'), data.get('conteudo'), id)
            )
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        if conn: conn.close()

# Rota para deletar um card (soft delete)
@knowledge_bp.route('/cards/<int:id>', methods=['DELETE'])
def delete_card(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE knowledge_cards SET status_id = 99 WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "success"})
    finally:
        if conn: conn.close()