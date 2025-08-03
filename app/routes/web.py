from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..services import storage
from ..services.prompt_builder import build_prompt
from ..services.llm import generate_from_gemini
from ..config import Config
import json, os

bp = Blueprint("web", __name__)

def load_meet_values():
    path = os.path.join(Config.DATA_DIR, "meet_values.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return ["Collaboration", "Respect", "Curiosity", "Coexistence", "Ownership"]

@bp.get("/")
def home():
    return render_template("home.html")

@bp.get("/upload")
def upload_page():
    return render_template("upload.html")

@bp.post("/upload")
def upload_action():
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Please choose a file.", "error")
        return redirect(url_for("web.upload_page"))
    content = f.read()
    if len(content) > Config.MAX_CONTENT_LENGTH:
        flash("File too large.", "error")
        return redirect(url_for("web.upload_page"))
    from ..services.extractor import extract_text
    kind, text = extract_text(f.filename, content)
    if not text.strip():
        flash("Could not extract text from the file.", "error")
        return redirect(url_for("web.upload_page"))
    sid = storage.create_session(f.filename, text, {"kind": kind})
    session["session_id"] = sid
    flash("Slides uploaded successfully!", "success")
    return redirect(url_for("web.configure_page"))

@bp.get("/configure")
def configure_page():
    sid = session.get("session_id")
    if not sid:
        return redirect(url_for("web.upload_page"))
    meet_values = load_meet_values()
    return render_template("configure.html", meet_values=meet_values)

@bp.post("/configure")
def configure_action():
    sid = session.get("session_id")
    if not sid:
        return redirect(url_for("web.upload_page"))

    instructor_style = request.form.getlist("instructor_style")
    requested_modes = request.form.getlist("requested_modes")
    post_DU = bool(request.form.get("post_DU"))
    last_session_of_day = bool(request.form.get("last_session_of_day"))
    mixed_skill = bool(request.form.get("mixed_skill"))
    instructor_count = int(request.form.get("instructor_count") or 1)
    custom_ideas = [s.strip() for s in (request.form.get("custom_ideas") or "").split(",") if s.strip()]
    meet_values = request.form.getlist("meet_values")

    session["config"] = {
        "instructor_style": instructor_style,
        "requested_modes": requested_modes or ["full-highlight-script"],
        "context_flags": {
            "post_DU": post_DU,
            "last_session_of_day": last_session_of_day,
            "mixed_skill": mixed_skill,
            "instructor_count": instructor_count
        },
        "custom_ideas": custom_ideas,
        "meet_values": meet_values
    }
    flash("Configuration saved.", "success")
    return redirect(url_for("web.generate_page"))

@bp.get("/generate")
def generate_page():
    sid = session.get("session_id")
    cfg = session.get("config")
    if not sid or not cfg:
        return redirect(url_for("web.upload_page"))
    sess = storage.load_session(sid)
    slides_text = sess["slides_text"]

    prompt = build_prompt(
        meet_values=cfg["meet_values"],
        slides_text=slides_text,
        instructor_style=cfg["instructor_style"],
        requested_modes=cfg["requested_modes"],
        context_flags=cfg["context_flags"],
        custom_ideas=cfg["custom_ideas"]
    )
    output = generate_from_gemini(prompt)

    # Persist a generated snapshot (simple)
    gen_id = storage.create_session(
        "generated",
        slides_text,
        {
            **cfg,
            "highlight_script": output
        }
    )
    return render_template("generate.html", output=output, gen_id=gen_id)

@bp.get("/session/<session_id>")
def session_view(session_id):
    try:
        data = storage.load_session(session_id)
    except FileNotFoundError:
        data = None
    return render_template("session.html", session_id=session_id, data=data)

@bp.get("/download/<session_id>")
def download_text(session_id):
    from flask import Response
    try:
        data = storage.load_session(session_id)
        txt = data["metadata"].get("highlight_script", "")
    except Exception:
        txt = ""
    return Response(
        txt or "No script available.",
        mimetype="text/plain",
        headers={"Content-Disposition": f'attachment; filename="script_{session_id}.txt"'}
    )
