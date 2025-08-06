import subprocess, tempfile, os, shutil, uuid
from .renderer import render_pdf_to_images

def pptx_to_images(file_bytes: bytes, session_id: str) -> list[str]:
    tmp_dir = tempfile.mkdtemp()
    pptx_path = os.path.join(tmp_dir, "slides.pptx")
    pdf_path  = os.path.join(tmp_dir, "slides.pdf")
    with open(pptx_path, "wb") as f: f.write(file_bytes)

    try:
        subprocess.check_call(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp_dir, pptx_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return render_pdf_to_images(pdf_bytes, session_id)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
