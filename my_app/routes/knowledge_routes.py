# /my_app/routes/knowledge_routes.py

from flask import Blueprint, request, jsonify
from ..db import get_db_connection

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

# --- ROTAS DOS CARDS ---

@knowledge_bp.route('/cards', methods=['GET'])
def get_cards():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, description FROM knowledge_cards ORDER BY title")
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
    description = data.get('description')
    if not title:
        return jsonify({"error": "O título é obrigatório"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO knowledge_cards (title, description) VALUES (%s, %s)", (title, description))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    if not title:
        return jsonify({"error": "O título é obrigatório"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE knowledge_cards SET title = %s, description = %s WHERE id = %s", (title, description, card_id))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Card não encontrado"}), 404)
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
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Card não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# --- ROTAS DOS TEMPLATES ---

@knowledge_bp.route('/templates', methods=['GET'])
def get_templates():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM knowledge_templates ORDER BY name")
            templates = cur.fetchall()
            
            # Para cada template, buscar os IDs dos cards associados na ordem correta
            for template in templates:
                cur.execute(
                    "SELECT card_id FROM knowledge_template_cards WHERE template_id = %s ORDER BY display_order",
                    (template['id'],)
                )
                # O resultado é uma lista de dicts, ex: [{'card_id': 1}, {'card_id': 3}]
                # Precisamos extrair apenas os valores para ter uma lista de IDs: [1, 3]
                card_ids_dicts = cur.fetchall()
                template['cards'] = [item['card_id'] for item in card_ids_dicts]
                
            return jsonify(templates)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/templates', methods=['POST'])
def create_template():
    data = request.get_json()
    name = data.get('name')
    card_ids = data.get('cards', [])
    if not name:
        return jsonify({"error": "O nome do template é obrigatório"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Inserir o template
            cur.execute("INSERT INTO knowledge_templates (name) VALUES (%s)", (name,))
            template_id = cur.lastrowid
            
            # Inserir os cards associados
            if card_ids:
                sql_values = []
                for index, card_id in enumerate(card_ids):
                    sql_values.append((template_id, card_id, index))
                
                cur.executemany(
                    "INSERT INTO knowledge_template_cards (template_id, card_id, display_order) VALUES (%s, %s, %s)",
                    sql_values
                )
            conn.commit()
            return jsonify({"status": "success", "id": template_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@knowledge_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    data = request.get_json()
    name = data.get('name')
    card_ids = data.get('cards', [])
    if not name:
        return jsonify({"error": "O nome do template é obrigatório"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Atualizar nome
            cur.execute("UPDATE knowledge_templates SET name = %s WHERE id = %s", (name, template_id))
            
            # Deletar associações antigas
            cur.execute("DELETE FROM knowledge_template_cards WHERE template_id = %s", (template_id,))

            # Inserir novas associações
            if card_ids:
                sql_values = []
                for index, card_id in enumerate(card_ids):
                    sql_values.append((template_id, card_id, index))
                
                cur.executemany(
                    "INSERT INTO knowledge_template_cards (template_id, card_id, display_order) VALUES (%s, %s, %s)",
                    sql_values
                )
            conn.commit()
            return jsonify({"status": "success"})
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
            # A tabela de ligação tem ON DELETE CASCADE, então não precisamos apagar manualmente
            cur.execute("DELETE FROM knowledge_templates WHERE id = %s", (template_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Template não encontrado"}), 404)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

# /my_app/routes/knowledge_routes.py

from flask import Blueprint, jsonify

knowledge_bp = Blueprint('knowledge_bp', __name__, url_prefix='/api/knowledge')

@knowledge_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok", module="Conhecimento"), 200