import os
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta


BASE_DIR = os.path.dirname(__file__)

class Config:
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    MAX_CONTENT_LENGTH_MB = float(os.getenv("MAX_CONTENT_LENGTH_MB", "25"))
    MAX_CONTENT_LENGTH = int(MAX_CONTENT_LENGTH_MB * 1024 * 1024)

    DATA_DIR = os.path.join(BASE_DIR, "data")
    SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")      # kept for legacy; not used when Firestore enabled
    TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts") # kept for legacy; not used when Firestore enabled

    STATIC_DIR = os.path.join(BASE_DIR, "static")
    UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")       # rendered slide images

    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # SMTP
    SMTP_SENDER_NAME = os.getenv("SMTP_SENDER_NAME", "MSSA")
    SMTP_FROM = os.getenv("SMTP_FROM", "")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

    # Firebase Admin (server)
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")

    # Firebase Web (client)
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_PROJECT_ID_WEB = os.getenv("FIREBASE_PROJECT_ID_WEB", "")
    FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID", "")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
