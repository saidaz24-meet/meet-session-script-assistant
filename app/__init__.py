from flask import Flask, render_template, jsonify
from flask_cors import CORS
from .config import ALLOWED_ORIGINS

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object("app.config.Config")

    # CORS (kept simple; you can tighten for prod)
    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS or "*"}})

    # Blueprints
    from .routes.web import bp as web_bp
    from .routes.api import bp as api_bp
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    # Simple error pages
    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", content="404 — Not Found"), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("base.html", content="File too large"), 413

    return app
