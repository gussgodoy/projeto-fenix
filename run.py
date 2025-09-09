# /projeto-fenix/run.py

from my_app import create_app

app = create_app()

if __name__ == '__main__':
    # O debug=True faz o servidor reiniciar automaticamente a cada mudança no código.
    app.run(debug=True, port=5000, host='0.0.0.0')