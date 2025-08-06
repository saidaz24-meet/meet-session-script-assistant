from flask import Flask, render_template, jsonify, g, session
from flask_cors import CORS
from .config import ALLOWED_ORIGINS, Config
from dotenv import load_dotenv
import os
from .services.firebase import init_firebase

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# ---------- Firebase Admin Safe Init ----------
if not firebase_admin._apps:  # ensures only runs once
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized ✅")
    else:
        print("WARNING: Firebase credentials not found or path invalid.")

# Create a global Firestore client
db = firestore.client()


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS or "*"}})

    init_firebase()


    @app.before_request
    def load_user():
        g.user = session.get("user")

    from .routes.web import bp as web_bp
    from .routes.api import bp as api_bp
    from .routes.auth import bp as auth_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.errorhandler(404)
    def nf(e):
        return render_template("base.html", content="404 — Not Found"), 404

    return app

