import os, fitz, uuid
from ..config import Config

def render_pdf_to_images(file_bytes: bytes, session_id: str) -> list[str]:
    """Return list of static paths (relative to /static) for rendered pages."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    outdir = os.path.join(Config.UPLOADS_DIR, session_id)
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=160)
        fname = f"page_{i+1:03d}.png"
        fpath = os.path.join(outdir, fname)
        pix.save(fpath)
        paths.append(f"/static/uploads/{session_id}/{fname}")
    return paths
