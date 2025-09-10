from flask import Blueprint, jsonify, request
from ..db import get_db_connection
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

def get_date_range(period):
    today = datetime.now()
    if period == 'hoje':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif period == 'ontem':
        start_date = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif period == 'semana':
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    elif period == 'mes':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    return start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')

@dashboard_bp.route('/data', methods=['GET'])
def get_dashboard_data():
    period = request.args.get('period', 'hoje')
    start_date_str, end_date_str = get_date_range(period)
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM conversations WHERE timestamp BETWEEN %s AND %s", (start_date_str, end_date_str))
            total_conversas = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as total FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE c.timestamp BETWEEN %s AND %s", (start_date_str, end_date_str))
            total_mensagens = cur.fetchone()['total']
            cur.execute("SELECT a.nome, COUNT(c.id) as total_conversas FROM conversations c JOIN agentes a ON c.agente_id = a.id WHERE c.timestamp BETWEEN %s AND %s GROUP BY a.nome ORDER BY total_conversas DESC", (start_date_str, end_date_str))
            conversas_por_agente = cur.fetchall()
            cur.execute("SELECT HOUR(timestamp) as hora, COUNT(*) as total FROM conversations WHERE timestamp BETWEEN %s AND %s GROUP BY hora ORDER BY hora", (start_date_str, end_date_str))
            atendimentos_por_hora = cur.fetchall()
            cur.execute("SELECT avaliacao, COUNT(*) as total FROM conversations WHERE avaliacao IS NOT NULL AND timestamp BETWEEN %s AND %s GROUP BY avaliacao", (start_date_str, end_date_str))
            avaliacoes = cur.fetchall()
            return jsonify({
                "kpis": {
                    "total_conversas": total_conversas,
                    "total_mensagens": total_mensagens,
                    "avaliacoes": {item['avaliacao']: item['total'] for item in avaliacoes}
                },
                "conversas_por_agente": conversas_por_agente,
                "atendimentos_por_hora": atendimentos_por_hora
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@dashboard_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="ok", module="Dashboard"), 200