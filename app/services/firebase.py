import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
from ..config import Config

# Global references
_app = None
_db = None

def init_firebase():
    global _app, _db
    if _app and _db:
        return _app, _db  # Already initialized

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS path is invalid or missing.")

    if not firebase_admin._apps:  # <-- Check the global firebase_admin registry
        print(f"Initializing Firebase with: {cred_path}")
        cred = credentials.Certificate(cred_path)
        _app = firebase_admin.initialize_app(cred, {
            "projectId": os.getenv("FIREBASE_PROJECT_ID", Config.FIREBASE_PROJECT_ID)
        })
    else:
        _app = firebase_admin.get_app()  # <-- Reuse existing app

    _db = firestore.client(_app)
    return _app, _db

def get_db():
    global _db
    if _db is None:
        _, _db = init_firebase()
    return _db

def verify_id_token(id_token: str) -> dict:
    if not id_token:
        raise ValueError("Missing idToken")
    init_firebase()  # Ensures _app exists
    return auth.verify_id_token(id_token)
