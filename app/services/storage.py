import uuid
import os
import json
from ..services.firebase import get_db
from ..config import Config

# Collections
COLL_SESSIONS = "sessions"
COLL_TRANSCRIPTS = "transcripts"

def _get_fallback_db():
    """Get fallback file-based storage when Firebase is not available"""
    return {
        "sessions_dir": os.path.join(Config.DATA_DIR, "sessions"),
        "transcripts_dir": os.path.join(Config.DATA_DIR, "transcripts")
    }

def _ensure_dirs():
    """Ensure storage directories exist"""
    fallback = _get_fallback_db()
    os.makedirs(fallback["sessions_dir"], exist_ok=True)
    os.makedirs(fallback["transcripts_dir"], exist_ok=True)

# ---- Sessions (LLM highlight scripts) ----
def session_create(name: str, payload: dict) -> str:
    db = get_db()
    sid = str(uuid.uuid4())
    
    if db is not None:
        try:
            doc = {"id": sid, "name": name, **payload}
            db.collection(COLL_SESSIONS).document(sid).set(doc)
            return sid
        except Exception as e:
            print(f"DEBUG: Firebase session creation failed, falling back to file storage: {e}")
    
    # Fallback to file storage
    _ensure_dirs()
    fallback = _get_fallback_db()
    doc = {"id": sid, "name": name, **payload}
    file_path = os.path.join(fallback["sessions_dir"], f"{sid}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return sid

def session_load(session_id: str) -> dict:
    db = get_db()
    
    if db is not None:
        try:
            doc = db.collection(COLL_SESSIONS).document(session_id).get()
            if not doc.exists:
                raise FileNotFoundError("Session not found")
            return doc.to_dict()
        except Exception as e:
            print(f"DEBUG: Firebase session load failed, trying file storage: {e}")
    
    # Fallback to file storage
    fallback = _get_fallback_db()
    file_path = os.path.join(fallback["sessions_dir"], f"{session_id}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError("Session not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def session_list() -> list[dict]:
    db = get_db()
    
    if db is not None:
        try:
            snaps = db.collection(COLL_SESSIONS).stream()
            return sorted([{"id": s.id} for s in snaps], key=lambda d: d["id"])
        except Exception as e:
            print(f"DEBUG: Firebase session list failed, trying file storage: {e}")
    
    # Fallback to file storage
    _ensure_dirs()
    fallback = _get_fallback_db()
    sessions = []
    for filename in os.listdir(fallback["sessions_dir"]):
        if filename.endswith(".json"):
            session_id = filename[:-5]  # Remove .json extension
            sessions.append({"id": session_id})
    return sorted(sessions, key=lambda d: d["id"])

def session_update(session_id: str, patch: dict):
    db = get_db()
    
    if db is not None:
        try:
            db.collection(COLL_SESSIONS).document(session_id).set(patch, merge=True)
            return
        except Exception as e:
            print(f"DEBUG: Firebase session update failed, trying file storage: {e}")
    
    # Fallback to file storage
    fallback = _get_fallback_db()
    file_path = os.path.join(fallback["sessions_dir"], f"{session_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        existing_data.update(patch)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

# ---- Transcripts (two-column Player) ----
def transcript_save(payload: list, tid: str | None = None) -> str:
    db = get_db()
    tid = tid or str(uuid.uuid4())
    
    if db is not None:
        try:
            doc = {"id": tid, "slides": payload}
            db.collection(COLL_TRANSCRIPTS).document(tid).set(doc)
            return tid
        except Exception as e:
            print(f"DEBUG: Firebase transcript save failed, falling back to file storage: {e}")
    
    # Fallback to file storage
    _ensure_dirs()
    fallback = _get_fallback_db()
    doc = {"id": tid, "slides": payload}
    file_path = os.path.join(fallback["transcripts_dir"], f"{tid}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return tid

def transcript_load(tid: str) -> list:
    db = get_db()
    
    if db is not None:
        try:
            snap = db.collection(COLL_TRANSCRIPTS).document(tid).get()
            if not snap.exists:
                raise FileNotFoundError("Transcript not found")
            data = snap.to_dict() or {}
            return data.get("slides", [])
        except Exception as e:
            print(f"DEBUG: Firebase transcript load failed, trying file storage: {e}")
    
    # Fallback to file storage
    fallback = _get_fallback_db()
    file_path = os.path.join(fallback["transcripts_dir"], f"{tid}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError("Transcript not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("slides", [])

def transcript_list() -> list[dict]:
    db = get_db()
    
    if db is not None:
        try:
            snaps = db.collection(COLL_TRANSCRIPTS).stream()
            return sorted([{"id": s.id} for s in snaps], key=lambda d: d["id"])
        except Exception as e:
            print(f"DEBUG: Firebase transcript list failed, trying file storage: {e}")
    
    # Fallback to file storage
    _ensure_dirs()
    fallback = _get_fallback_db()
    transcripts = []
    for filename in os.listdir(fallback["transcripts_dir"]):
        if filename.endswith(".json"):
            transcript_id = filename[:-5]  # Remove .json extension
            transcripts.append({"id": transcript_id})
    return sorted(transcripts, key=lambda d: d["id"])
