import os, json, base64
import firebase_admin
from firebase_admin import credentials, auth, firestore
from ..config import Config

# Global references
_app = None
_db = None

def _load_cred():
    """
    Load Firebase Admin credentials from one of:
      1. FIREBASE_SERVICE_ACCOUNT_B64 (base64-encoded JSON)
      2. FIREBASE_SERVICE_ACCOUNT_JSON (raw JSON string)
      3. GOOGLE_APPLICATION_CREDENTIALS (file path to JSON)
    """
    b64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_B64", "").strip()
    if b64:
        # Decode base64 → JSON
        data = json.loads(base64.b64decode(b64).decode("utf-8"))
        return credentials.Certificate(data)

    raw_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
    if raw_json:
        # Parse JSON directly
        data = json.loads(raw_json)
        return credentials.Certificate(data)

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if cred_path and os.path.exists(cred_path):
        # Use local JSON file (dev only)
        return credentials.Certificate(cred_path)

    raise RuntimeError("No Firebase service account provided. "
                       "Set FIREBASE_SERVICE_ACCOUNT_B64, FIREBASE_SERVICE_ACCOUNT_JSON, "
                       "or GOOGLE_APPLICATION_CREDENTIALS path.")

def init_firebase():
    global _app, _db
    if _app and _db:
        return _app, _db  # Already initialized

    # Load credentials from env
    cred = _load_cred()

    if not firebase_admin._apps:  # First-time init
        print("Initializing Firebase Admin with env-based credentials ✅")
        _app = firebase_admin.initialize_app(cred, {
            "projectId": os.getenv("FIREBASE_PROJECT_ID", Config.FIREBASE_PROJECT_ID)
        })
    else:
        _app = firebase_admin.get_app()  # Reuse existing app

    # Initialize Firestore client
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
    init_firebase()  # Ensure app is initialized
    return auth.verify_id_token(id_token)
