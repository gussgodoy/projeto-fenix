# Dentro de my_app/__init__.py

@app.route('/health')
def health_check():
    db_status = "ok"
    try:
        conn = get_db_connection()
        conn.close()
    except Exception as e:
        db_status = f"error: {e}"
    
    return jsonify(
        server_status="OK",
        database_status=db_status
    )