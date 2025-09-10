# my_app/routes/status_routes.py

from flask import Blueprint, jsonify
from my_app.db import get_db_connection

status_bp = Blueprint('status', __name__)
APP_VERSION = "21.0 (Refactored)"

@status_bp.route('/')
def index():
    return f"<h1>O servidor Fênix está no ar! Versão: {APP_VERSION}</h1>"

@status_bp.route('/health', methods=['GET'])
def server_health_check():
    conn = None
    try:
        conn = get_db_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    finally:
        if conn:
            conn.close()
    return jsonify({"server_status": "OK", "app_version": APP_VERSION, "database_status": db_status}), 200