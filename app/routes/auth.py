from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..config import Config
from ..services.firebase import verify_id_token
from werkzeug.security import check_password_hash, generate_password_hash


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
    
    if not id_token:
        print("DEBUG: No idToken provided in session creation request")
        return {"detail": "Missing idToken"}, 400
    
    try:
        print(f"DEBUG: Verifying ID token...")
        decoded = verify_id_token(id_token)
        print(f"DEBUG: Token verified successfully for user: {decoded.get('uid')}")
        
        session["user"] = {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "name" : decoded.get("name") or decoded.get("displayName") or ""
        }
        session.permanent = True
        
        print(f"DEBUG: Session created for user: {session['user']['email']}")
        return {"ok": True}
        
    except Exception as e:
        print(f"DEBUG: Session creation failed: {str(e)}")
        return {"detail": str(e)}, 401

@bp.get("/logout")
def logout():
    session.pop("user", None)
    flash("Signed out.", "success")
    return redirect(url_for("web.home"))
