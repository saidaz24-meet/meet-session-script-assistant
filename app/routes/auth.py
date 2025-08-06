from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..config import Config
from ..services.firebase import verify_id_token

bp = Blueprint("auth", __name__, template_folder="../templates")

@bp.get("/login")
def login_page():
    return render_template("login.html",
                           fb_api_key=Config.FIREBASE_API_KEY,
                           fb_auth_domain=Config.FIREBASE_AUTH_DOMAIN,
                           fb_project_id=Config.FIREBASE_PROJECT_ID_WEB,
                           fb_app_id=Config.FIREBASE_APP_ID,
                           fb_sender_id=Config.FIREBASE_MESSAGING_SENDER_ID)

@bp.get("/signup")
def signup_page():
    return render_template("signup.html",
                           fb_api_key=Config.FIREBASE_API_KEY,
                           fb_auth_domain=Config.FIREBASE_AUTH_DOMAIN,
                           fb_project_id=Config.FIREBASE_PROJECT_ID_WEB,
                           fb_app_id=Config.FIREBASE_APP_ID,
                           fb_sender_id=Config.FIREBASE_MESSAGING_SENDER_ID)

# Client signs in with Firebase, gets idToken and posts here:
@bp.post("/session")
def create_session():
    data = request.get_json(silent=True) or {}
    id_token = data.get("idToken", "")
    try:
        decoded = verify_id_token(id_token)
        session["user"] = {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "name": decoded.get("name") or decoded.get("email")
        }
        return {"ok": True}
    except Exception as e:
        return {"detail": str(e)}, 401

@bp.get("/logout")
def logout():
    session.pop("user", None)
    flash("Signed out.", "success")
    return redirect(url_for("web.home"))
