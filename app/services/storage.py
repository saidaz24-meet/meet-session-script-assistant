import uuid
from ..services.firebase import get_db

# Collections
COLL_SESSIONS = "sessions"
COLL_TRANSCRIPTS = "transcripts"

# ---- Sessions (LLM highlight scripts) ----
def session_create(name: str, payload: dict) -> str:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    sid = str(uuid.uuid4())
    doc = {"id": sid, "name": name, **payload}
    db.collection(COLL_SESSIONS).document(sid).set(doc)
    return sid

def session_load(session_id: str) -> dict:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    doc = db.collection(COLL_SESSIONS).document(session_id).get()
    if not doc.exists:
        raise FileNotFoundError("Session not found")
    return doc.to_dict()

def session_list() -> list[dict]:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    snaps = db.collection(COLL_SESSIONS).stream()
    return sorted([{"id": s.id} for s in snaps], key=lambda d: d["id"])

def session_update(session_id: str, patch: dict):
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    db.collection(COLL_SESSIONS).document(session_id).set(patch, merge=True)

# ---- Transcripts (two-column Player) ----
def transcript_save(payload: list, tid: str | None = None) -> str:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    tid = tid or str(uuid.uuid4())
    doc = {"id": tid, "slides": payload}
    db.collection(COLL_TRANSCRIPTS).document(tid).set(doc)
    return tid

def transcript_load(tid: str) -> list:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    snap = db.collection(COLL_TRANSCRIPTS).document(tid).get()
    if not snap.exists:
        raise FileNotFoundError("Transcript not found")
    data = snap.to_dict() or {}
    return data.get("slides", [])

def transcript_list() -> list[dict]:
    db = get_db()
    if db is None:
        raise RuntimeError("Firebase database not initialized. Please check your GOOGLE_APPLICATION_CREDENTIALS and FIREBASE_PROJECT_ID environment variables.")
    snaps = db.collection(COLL_TRANSCRIPTS).stream()
    return sorted([{"id": s.id} for s in snaps], key=lambda d: d["id"])
