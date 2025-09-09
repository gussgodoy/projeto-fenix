# /my_app/routes/escritorio_routes.py

from flask import Blueprint, request, jsonify
from ..db import get_db_connection

escritorio_bp = Blueprint('escritorio', __name__, url_prefix='/api/escritorio')

# --- ROTAS DE CLIENTES ---

@escritorio_bp.route('/clientes', methods=['GET'])
def get_clientes():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Seleciona todos os campos necessários para a exibição e o formulário
            cur.execute("""
                SELECT 
                    c.*, 
                    s.name as status_nome, 
                    s.color as status_cor
                FROM clientes c
                JOIN statuses s ON c.status_id = s.id
                ORDER BY c.nome
            """)
            clientes = cur.fetchall()
            return jsonify(clientes)
    except Exception as e:
        print(f"Erro em get_clientes: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # SQL dinâmico para inserir apenas os campos fornecidos
            fields = [key for key in data if key in [
                'nome', 'razao_social', 'cnpj', 'website', 'status_id', 
                'contato_nome', 'contato_cargo', 'contato_telefone', 'contato_email', 
                'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
                'numero_contrato', 'valor_mensal', 'dia_de_vencimento', 
                'captador_id', 'indicador_id'
            ]]
            
            # Converte valores vazios para None (NULL no banco)
            values = []
            for field in fields:
                value = data.get(field)
                values.append(value if value != '' else None)

            placeholders = ', '.join(['%s'] * len(fields))
            sql = f"INSERT INTO clientes ({', '.join(fields)}) VALUES ({placeholders})"
            
            cur.execute(sql, tuple(values))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    except Exception as e:
        print(f"Erro em create_cliente: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            fields = [key for key in data if key != 'id']
            
            set_clauses = []
            values = []
            for field in fields:
                value = data.get(field)
                set_clauses.append(f"{field} = %s")
                values.append(value if value != '' else None)
            
            values.append(cliente_id) # Adiciona o ID para a cláusula WHERE
            
            sql = f"UPDATE clientes SET {', '.join(set_clauses)} WHERE id = %s"
            
            cur.execute(sql, tuple(values))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Cliente não encontrado"}), 404)
    except Exception as e:
        print(f"Erro em update_cliente: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@escritorio_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Cliente não encontrado"}), 404)
    except Exception as e:
        print(f"Erro em delete_cliente: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()