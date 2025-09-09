# /projeto-fenix/my_app/routes/configuracoes.py

from flask import Blueprint, request, jsonify
from my_app.db import get_db_connection
import uuid

config_bp = Blueprint('configuracoes', __name__, url_prefix='/api/config')

# --- ROTAS PARA PROVEDORES DE IA ---

@config_bp.route('/provedores', methods=['GET', 'POST'])
def handle_provedores():
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Erro de conexão com o banco de dados."}), 500
    
    try:
        cursor = conn.cursor()
        if request.method == 'GET':
            cursor.execute("""
                SELECT p.id, p.nome, p.status_id, s.nome as status, s.cor, COUNT(pc.id) as chaves_count
                FROM provedores p
                JOIN status s ON p.status_id = s.id
                LEFT JOIN provedor_chaves pc ON p.id = pc.provedor_id
                GROUP BY p.id, p.nome, p.status_id, s.nome, s.cor
                ORDER BY p.nome ASC
            """)
            provedores = [dict(row) for row in cursor.fetchall()]
            return jsonify(provedores)
        
        if request.method == 'POST':
            data = request.get_json()
            nome = data.get('nome')
            if not nome or not nome.strip(): 
                return jsonify({"message": "O campo 'nome' é obrigatório."}), 400
            
            cursor.execute("INSERT INTO provedores (nome) VALUES (%s)", (nome,))
            conn.commit()
            return jsonify({"status": "success", "message": "Provedor criado com sucesso."}), 201
    finally:
        if conn: conn.close()

@config_bp.route('/provedores/<int:id>', methods=['DELETE'])
def delete_provedor_by_id(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM provedores WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Provedor não encontrado."}), 404
    finally:
        if conn: conn.close()
        
@config_bp.route('/provedores/<int:id>/status', methods=['PUT'])
def update_provedor_status(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        data = request.get_json()
        status_id = data.get('status_id')
        if status_id is None:
            return jsonify({"message": "'status_id' é obrigatório."}), 400
            
        cursor = conn.cursor()
        cursor.execute("UPDATE provedores SET status_id = %s WHERE id = %s", (status_id, id))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Provedor não encontrado."}), 404
    finally:
        if conn: conn.close()

# --- ROTAS PARA CHAVES DOS PROVEDORES DE IA ---

@config_bp.route('/provedores/<int:provedor_id>/chaves', methods=['GET', 'POST'])
def handle_provedor_chaves(provedor_id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        if request.method == 'GET':
            cursor.execute("""
                SELECT pc.id, pc.nome, pc.api_key, pc.modelo, pc.status_id, s.nome as status, s.cor 
                FROM provedor_chaves pc
                JOIN status s ON pc.status_id = s.id
                WHERE pc.provedor_id = %s
            """, (provedor_id,))
            chaves = [dict(row) for row in cursor.fetchall()]
            return jsonify(chaves)
        if request.method == 'POST':
            data = request.get_json()
            nome = data.get('nome')
            api_key = data.get('api_key')
            modelo = data.get('modelo')
            if not api_key or not nome:
                return jsonify({"message": "'Nome da Chave' e 'API Key' são obrigatórios."}), 400
            cursor.execute(
                "INSERT INTO provedor_chaves (provedor_id, nome, api_key, modelo) VALUES (%s, %s, %s, %s)",
                (provedor_id, nome, api_key, modelo)
            )
            conn.commit()
            return jsonify({"status": "success"}), 201
    finally:
        if conn: conn.close()

@config_bp.route('/provedores/chaves/<int:id>', methods=['DELETE'])
def delete_provedor_chave_by_id(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM provedor_chaves WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Chave não encontrada."}), 404
    finally:
        if conn: conn.close()

@config_bp.route('/provedores/chaves/<int:id>/status', methods=['PUT'])
def update_provedor_chave_status(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        data = request.get_json()
        status_id = data.get('status_id')
        if status_id is None:
            return jsonify({"message": "'status_id' é obrigatório."}), 400
        cursor = conn.cursor()
        cursor.execute("UPDATE provedor_chaves SET status_id = %s WHERE id = %s", (status_id, id))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Chave não encontrada."}), 404
    finally:
        if conn: conn.close()

# --- ROTAS PARA CHAVES DA NOSSA API FÊNIX ---

@config_bp.route('/chaves-api', methods=['GET', 'POST'])
def handle_chaves_api():
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        if request.method == 'GET':
            cursor.execute("""
                SELECT ca.id, ca.nome, ca.chave, ca.status_id, s.nome as status, s.cor, 
                       DATE_FORMAT(ca.data_criacao, '%d/%m/%Y') as data_criacao 
                FROM chaves_api ca
                JOIN status s ON ca.status_id = s.id
                ORDER BY ca.id DESC
            """)
            chaves = [dict(row) for row in cursor.fetchall()]
            return jsonify(chaves)
        if request.method == 'POST':
            data = request.get_json()
            nome = data.get('nome')
            if not nome or not nome.strip(): 
                return jsonify({"message": "O campo 'nome' é obrigatório."}), 400
            nova_chave = f"fenix-{uuid.uuid4()}"
            cursor.execute("INSERT INTO chaves_api (nome, chave) VALUES (%s, %s)", (nome, nova_chave))
            conn.commit()
            return jsonify({"status": "success", "id": cursor.lastrowid}), 201
    finally:
        if conn: conn.close()

@config_bp.route('/chaves-api/<int:id>', methods=['DELETE'])
def delete_chave_api_by_id(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chaves_api WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Chave da API não encontrada."}), 404
    finally:
        if conn: conn.close()

@config_bp.route('/chaves-api/<int:id>/status', methods=['PUT'])
def update_chave_api_status(id):
    conn = get_db_connection()
    if not conn: return jsonify({"message": "Erro de conexão"}), 500
    try:
        data = request.get_json()
        status_id = data.get('status_id')
        if status_id is None:
            return jsonify({"message": "'status_id' é obrigatório."}), 400
        cursor = conn.cursor()
        cursor.execute("UPDATE chaves_api SET status_id = %s WHERE id = %s", (status_id, id))
        conn.commit()
        return jsonify({"status": "success"}) if cursor.rowcount > 0 else jsonify({"message": "Chave da API não encontrada."}), 404
    finally:
        if conn: conn.close()

# --- ROTAS PARA CANAIS --- 
@config_bp.route('/canais', methods=['GET'])
def get_canais():
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Erro de conexão com o banco de dados."}), 500
    try:
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM provedores_canais")
        canais = [dict(row) for row in cursor.fetchall()]
        return jsonify(canais)
    finally:
        if conn:
            conn.close()