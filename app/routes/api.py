from flask import Blueprint, request, jsonify
from ..services.extractor import extract_text
from ..services.prompt_builder import build_prompt
from ..services.llm import generate_from_gemini
from ..services import storage
from ..config import Config
import re

bp = Blueprint("api", __name__)

def parse_missing_support(text: str):
    ms = {"slides_needed": [], "props": []}
    m = re.search(r"Missing support.*", text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return ms
    block = m.group(0)
    slides = re.findall(r"slides_needed\s*:\s*\[([^\]]*)\]", block)
    props = re.findall(r"props\s*:\s*\[([^\]]*)\]", block)
    if slides:
        ms["slides_needed"] = [s.strip().strip('"\'' ) for s in slides[0].split(",") if s.strip()]
    if props:
        ms["props"] = [p.strip().strip('"\'' ) for p in props[0].split(",") if p.strip()]
    return ms

@bp.post("/files/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"detail": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"detail": "Empty filename"}), 400
    file_bytes = f.read()
    if len(file_bytes) > Config.MAX_CONTENT_LENGTH:
        return jsonify({"detail": "File too large"}), 413
    kind, text = extract_text(f.filename, file_bytes)
    if not text.strip():
        return jsonify({"detail": "Unable to extract text"}), 400
    session_id = storage.create_session(name=f.filename, slides_text=text, metadata={"kind": kind})
    return jsonify({"session_id": session_id, "chars": len(text)})

@bp.get("/sessions/<session_id>")
def get_session(session_id):
    try:
        data = storage.load_session(session_id)
        return jsonify({"session_id": session_id, "data": data})
    except FileNotFoundError:
        return jsonify({"detail": "Session not found"}), 404

@bp.post("/generate")
def generate():
    data = request.get_json(silent=True) or {}

    slides_text = data.get("slides_text", "")
    if not slides_text.strip():
        return jsonify({"detail": "slides_text is required"}), 400

    instructor_style = data.get("instructor_style", [])
    requested_modes = data.get("requested_modes", ["full-highlight-script"])
    context_flags = data.get("context_flags", {"post_DU": False,"last_session_of_day": False,"mixed_skill": True,"instructor_count": 1})
    custom_ideas = data.get("custom_ideas", [])
    meet_values = data.get("meet_values", [])

    prompt = build_prompt(
        meet_values=meet_values,
        slides_text=slides_text,
        instructor_style=instructor_style,
        requested_modes=requested_modes,
        context_flags=context_flags,
        custom_ideas=custom_ideas
    )

    output = generate_from_gemini(prompt)
    if not output.strip():
        return jsonify({"detail": "Empty response from LLM"}), 502

    session_id = storage.create_session(
        name="generated",
        slides_text=slides_text,
        metadata={
            "instructor_style": instructor_style,
            "requested_modes": requested_modes,
            "context_flags": context_flags,
            "custom_ideas": custom_ideas,
            "meet_values": meet_values,
            "highlight_script": output
        }
    )
    
    ms = parse_missing_support(output)
    return jsonify({"session_id": session_id, "highlight_script": output, "missing_support": ms})
