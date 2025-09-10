# my_app/routes/status_routes.py
from flask import Blueprint, jsonify

status_bp = Blueprint('status', __name__)

@status_bp.route('/', methods=['GET'])
def get_status():
    return jsonify({"status": "ok", "message": "API está no ar."})