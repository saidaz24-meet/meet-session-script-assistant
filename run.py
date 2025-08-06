from app import create_app
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import firestore

try:
    db = firestore.client()
    print("DEBUG: Firestore connected! Collections:", list(db.collections()))
except Exception as e:
    print("DEBUG: Firestore connection failed ->", e)


# Load environment variables
load_dotenv()
print("DEBUG: GOOGLE_APPLICATION_CREDENTIALS =", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))


app = create_app()

if __name__ == "__main__":
    # Use Flask's dev server; for prod, use gunicorn/uvicorn behind nginx.
    app.run(host="127.0.0.1", port=5000, debug=True)
