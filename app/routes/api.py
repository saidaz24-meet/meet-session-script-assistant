from flask import Blueprint, request, jsonify
from ..services import storage, emailer, llm
from ..services.extractor import extract_text, extract_structured
from ..services.converter import pptx_to_images
from ..services.renderer import render_pdf_to_images
from ..services.prompt_builder import build_highlight_prompt
from ..config import Config
import re, json
import traceback


bp = Blueprint("api", __name__)

# ---------- Slide/LLM flow ----------
@bp.post("/files/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({"detail": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"detail": "Empty filename"}), 400
    content = f.read()
    if len(content) > Config.MAX_CONTENT_LENGTH:
        return jsonify({"detail": "File too large"}), 413
    kind, text, slide_texts = extract_structured(f.filename, content)
    if not text.strip() and not any(slide_texts):
        return jsonify({"detail": "Unable to extract text"}), 400
    sid = storage.session_create(
        name=f.filename,
        payload={"slides_text": text, "slide_texts": slide_texts, "metadata": {"kind": kind}}
    )
    paths = []
    if kind == "pdf":
        paths = render_pdf_to_images(content, sid)
    elif kind == "pptx":
        paths = pptx_to_images(content, sid)
    if paths:
        storage.session_update(sid, {"images": paths})
    return jsonify({"session_id": sid, "chars": len(text), "images": paths, "slides": len(slide_texts)})


@bp.get("/sessions/<session_id>")
def get_session(session_id):
    try:
        return jsonify(storage.session_load(session_id))
    except FileNotFoundError:
        return jsonify({"detail": "Session not found"}), 404

def _parse_missing_support(text: str):
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

@bp.post("/generate")
def generate_highlight_script():
    data = request.get_json(silent=True) or {}
    slides_text = data.get("slides_text", "")
    if not slides_text.strip():
        return jsonify({"detail": "slides_text is required"}), 400

    # fields from UI
    instructor_style = data.get("instructor_style", [])
    requested_modes = data.get("requested_modes", ["full-highlight-script"])
    context_flags = data.get("context_flags", {"post_DU": False,"last_session_of_day": False,"mixed_skill": True,"instructor_count": 1})
    custom_ideas = data.get("custom_ideas", [])
    meet_values = data.get("meet_values", [])

    prompt = build_highlight_prompt(
        meet_values, slides_text, instructor_style,
        requested_modes, context_flags, custom_ideas
    )
    output = llm.gemini_generate(prompt)
    if not output.strip():
        return jsonify({"detail": "Empty response from LLM"}), 502

    sid = storage.session_create(
        name="generated",
        payload={
            "slides_text": slides_text,
            "config": {
                "instructor_style": instructor_style,
                "requested_modes": requested_modes,
                "context_flags": context_flags,
                "custom_ideas": custom_ideas,
                "meet_values": meet_values
            },
            "highlight_script": output
        }
    )
    ms = _parse_missing_support(output)
    return jsonify({"session_id": sid, "highlight_script": output, "missing_support": ms})

# ---------- Transcript CRUD ----------
@bp.get("/transcripts")
def list_transcripts():
    return jsonify(storage.transcript_list())

@bp.get("/transcripts/<tid>")
def get_transcript(tid):
    try:
        return jsonify(storage.transcript_load(tid))
    except FileNotFoundError:
        return jsonify({"detail": "Not found"}), 404

@bp.post("/transcripts")
def create_transcript():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, list):
        return jsonify({"detail":"Expected a list of slides"}), 400
    tid = storage.transcript_save(payload)
    return jsonify({"id": tid})

@bp.put("/transcripts/<tid>")
def update_transcript(tid):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, list):
        return jsonify({"detail":"Expected a list of slides"}), 400
    storage.transcript_save(payload, tid)
    return jsonify({"id": tid, "updated": True})

# ---------- Email ----------
@bp.post("/email")
def send_email():
    data = request.get_json(silent=True) or {}
    to_email = data.get("to")
    subject = data.get("subject", "MEET Session Transcript")
    html = data.get("html", "")
    if not (to_email and html.strip()):
        return jsonify({"detail": "to & html required"}), 400
    try:
        emailer.send_email(to_email, subject, html)
        return jsonify({"ok": True})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"detail": str(e)}), 500

# ---------- Chat condense (stub) ----------
@bp.post("/chat/condense")
def chat_condense():
    data = request.get_json(silent=True) or {}
    msgs = data.get("messages", [])
    prompt = llm.gemini_condense_chat(msgs)
    return jsonify({"prompt": prompt})

