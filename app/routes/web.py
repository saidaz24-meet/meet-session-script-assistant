from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from ..services import storage
from ..services.prompt_builder import build_highlight_prompt
from ..services.llm import gemini_generate
from ..config import Config
import json, os, re

bp = Blueprint("web", __name__)

def load_meet_values():
    path = os.path.join(Config.DATA_DIR, "meet_values.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return ["Collaboration", "Respect", "Curiosity", "Coexistence", "Ownership"]

def _require_login():
    if not session.get("user"):
        flash("Please sign in.", "error")
        return False
    return True

@bp.get("/")
def home():
    return render_template("home.html")

# ---------- Slide/LLM flow ----------
@bp.get("/upload")
def upload_page():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    return render_template("upload.html")

@bp.post("/upload")
def upload_action():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Please choose a file.", "error")
        return redirect(url_for("web.upload_page"))
    content = f.read()
    if len(content) > Config.MAX_CONTENT_LENGTH:
        flash("File too large.", "error")
        return redirect(url_for("web.upload_page"))

    from ..services.extractor import extract_structured
    from ..services.renderer import render_pdf_to_images
    from ..services.converter import pptx_to_images
    from ..services import storage

    kind, text, slide_texts = extract_structured(f.filename, content)
    if not text.strip() and not any(slide_texts):
        flash("Could not extract text.", "error")
        return redirect(url_for("web.upload_page"))

    sid = storage.session_create(
        name=f.filename,
        payload={"slides_text": text, "slide_texts": slide_texts, "metadata": {"kind": kind}}
    )
    session["session_id"] = sid

    # Render images for PDF/PPTX and save to Firestore
    paths = []
    try:
        if kind == "pdf":
            paths = render_pdf_to_images(content, sid)
        elif kind == "pptx":
            paths = pptx_to_images(content, sid)
    except Exception as e:
        flash(f"Slide images not generated ({e}). You can still continue.", "error")

    if paths:
        storage.session_update(sid, {"images": paths})

    flash("Slides uploaded successfully!", "success")
    return redirect(url_for("web.configure_page"))


@bp.get("/configure")
def configure_page():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    if "session_id" not in session:
        return redirect(url_for("web.upload_page"))
    meet_values = load_meet_values()
    return render_template("configure.html", meet_values=meet_values)

@bp.post("/configure")
def configure_action():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    if "session_id" not in session:
        return redirect(url_for("web.upload_page"))

    instructor_style = request.form.getlist("instructor_style")
    requested_modes = request.form.getlist("requested_modes")
    post_DU = bool(request.form.get("post_DU"))
    last_session_of_day = bool(request.form.get("last_session_of_day"))
    mixed_skill = bool(request.form.get("mixed_skill"))
    instructor_count = int(request.form.get("instructor_count") or 1)
    custom_ideas = [s.strip() for s in (request.form.get("custom_ideas") or "").split(",") if s.strip()]

    # NEW: free-text per section
    free_text_notes = []
    free_text_notes.append(request.form.get("free_text_styles",""))
    free_text_notes.append(request.form.get("free_text_modes",""))
    free_text_notes.append(request.form.get("free_text_context",""))
    free_text_notes.append(request.form.get("free_text_values",""))

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
        "meet_values": meet_values,
        "free_text_notes": free_text_notes
    }
    flash("Configuration saved.", "success")
    return redirect(url_for("web.generate_page"))

@bp.get("/generate")
def generate_page():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    if "session_id" not in session or "config" not in session:
        return redirect(url_for("web.upload_page"))
    sid = session["session_id"]
    cfg = session["config"]
    sess = storage.session_load(sid)
    slides_text = sess.get("slides_text", "")
    slide_texts = sess.get("slide_texts", []) or []
    images = sess.get("images", [])  # may be empty

    from ..services.prompt_builder import (
        ai_refine_notes,
        build_highlight_prompt,
        build_slide_aligned_prompt,
    )

    refined_notes = ai_refine_notes(cfg.get("free_text_notes", []))

    # Prefer slide-aligned prompt if we have per-slide texts
    if slide_texts:
        prompt = build_slide_aligned_prompt(
            meet_values=cfg["meet_values"],
            slide_texts=slide_texts,
            instructor_style=cfg["instructor_style"],
            requested_modes=cfg["requested_modes"],
            context_flags=cfg["context_flags"],
            custom_ideas=cfg["custom_ideas"],
            free_text_notes=refined_notes
        )
    else:
        prompt = build_highlight_prompt(
            meet_values=cfg["meet_values"],
            slides_text=slides_text,
            instructor_style=cfg["instructor_style"],
            requested_modes=cfg["requested_modes"],
            context_flags=cfg["context_flags"],
            custom_ideas=cfg["custom_ideas"],
            free_text_notes=refined_notes
        )

    output = gemini_generate(prompt)
    gen_id = storage.session_create("generated", {
        "slides_text": slides_text,
        "slide_texts": slide_texts,
        "config": cfg,
        "highlight_script": output,
        "images": images
    })
    return render_template("viewer.html", output=output, images=images, session_id=gen_id)

# ---------- Transcript Editor/Player ----------
@bp.get("/editor")
def editor():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    sample_path = os.path.join(Config.DATA_DIR, "sample_transcript.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        sample = json.load(f)
    return render_template("editor.html", initial=json.dumps(sample, ensure_ascii=False, indent=2))

@bp.post("/editor/save")
def editor_save():
    if not _require_login(): return redirect(url_for("auth.login_page"))
    raw = request.form.get("json_input", "")
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("Root must be a list.")
    except Exception as e:
        flash(f"Invalid JSON: {e}", "error")
        return redirect(url_for("web.editor"))
    tid = storage.transcript_save(data)
    flash("Saved transcript.", "success")
    return redirect(url_for("web.player", tid=tid))

@bp.get("/player/<tid>")
def player(tid):
    if not _require_login(): return redirect(url_for("auth.login_page"))
    try:
        slides = storage.transcript_load(tid)
    except FileNotFoundError:
        slides = []
    return render_template("player.html", tid=tid, slides_json=json.dumps(slides, ensure_ascii=False))
