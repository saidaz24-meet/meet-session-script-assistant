from app import create_app

app = create_app()

if __name__ == "__main__":
    # Use Flask's dev server; for prod, use gunicorn/uvicorn behind nginx.
    app.run(host="127.0.0.1", port=5000, debug=True)
