import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(__file__)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
    MAX_CONTENT_LENGTH_MB = float(os.getenv("MAX_CONTENT_LENGTH_MB", "25"))
    MAX_CONTENT_LENGTH = int(MAX_CONTENT_LENGTH_MB * 1024 * 1024)

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5000,http://localhost:5000").split(",")

# Ensure folders exist
os.makedirs(Config.SESSIONS_DIR, exist_ok=True)
