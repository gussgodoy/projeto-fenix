# /my_app/routes/config_routes.py

import secrets
import json
from flask import Blueprint, request, jsonify
from ..db import get_db_connection

config_bp = Blueprint('config', __name__, url_prefix='/api/config')

# ... (código existente para /health, /statuses, /our-keys, /ia/providers, /ia/keys) ...
# ... (cole todo o código que já existe nessas seções aqui) ...

# --- ROTAS DE PERFIS DE IA ---

@config_bp.route('/perfis', methods=['GET'])
def get_perfis():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, config_avancada FROM perfis ORDER BY nome")
            perfis = cur.fetchall()
            for perfil in perfis:
                if perfil['config_avancada'] and isinstance(perfil['config_avancada'], str):
                    perfil['config_avancada'] = json.loads(perfil['config_avancada'])
            return jsonify(perfis)
    finally:
        if conn: conn.close()

@config_bp.route('/perfis', methods=['POST'])
def create_perfil():
    data = request.get_json()
    nome = data.get('nome')
    config = data.get('config_avancada')
    if not nome:
        return jsonify({"error": "O nome é obrigatório"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            config_str = json.dumps(config) if config else None
            cur.execute("INSERT INTO perfis (nome, config_avancada) VALUES (%s, %s)", (nome, config_str))
            conn.commit()
            return jsonify({"status": "success", "id": cur.lastrowid}), 201
    finally:
        if conn: conn.close()

@config_bp.route('/perfis/<int:perfil_id>', methods=['PATCH'])
def update_perfil(perfil_id):
    data = request.get_json()
    nome = data.get('nome')
    config = data.get('config_avancada')
    if not nome:
        return jsonify({"error": "O nome é obrigatório"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            config_str = json.dumps(config) if config else None
            cur.execute("UPDATE perfis SET nome = %s, config_avancada = %s WHERE id = %s", (nome, config_str, perfil_id))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Perfil não encontrado"}), 404)
    finally:
        if conn: conn.close()

@config_bp.route('/perfis/<int:perfil_id>', methods=['DELETE'])
def delete_perfil(perfil_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM perfis WHERE id = %s", (perfil_id,))
            conn.commit()
            return jsonify({"status": "success"}) if cur.rowcount > 0 else (jsonify({"error": "Perfil não encontrado"}), 404)
    finally:
        if conn: conn.close()