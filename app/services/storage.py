import json, os, uuid, orjson
from ..config import Config

def _path(session_id: str) -> str:
    return os.path.join(Config.SESSIONS_DIR, f"{session_id}.json")

def create_session(name: str, slides_text: str, metadata=None) -> str:
    session_id = str(uuid.uuid4())
    data = {"name": name, "slides_text": slides_text, "metadata": metadata or {}}
    with open(_path(session_id), "wb") as f:
        f.write(orjson.dumps(data))
    return session_id

def load_session(session_id: str) -> dict:
    with open(_path(session_id), "rb") as f:
        return orjson.loads(f.read())

def save_session(session_id: str, data: dict):
    with open(_path(session_id), "wb") as f:
        f.write(orjson.dumps(data))
