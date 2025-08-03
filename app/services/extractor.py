from typing import Tuple
from pdfminer.high_level import extract_text as pdf_extract
import fitz  # PyMuPDF
from pptx import Presentation
import io

def extract_from_pdf(file_bytes: bytes) -> str:
    # Try pdfminer; fallback to PyMuPDF for tricky docs.
    try:
        return pdf_extract(io.BytesIO(file_bytes))
    except Exception:
        text = []
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text.append(page.get_text())
        return "\n".join(text)

def extract_from_pptx(file_bytes: bytes) -> str:
    prs = Presentation(io.BytesIO(file_bytes))
    chunks = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                chunks.append(shape.text)
    return "\n".join(chunks)

def extract_text(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    name = filename.lower()
    if name.endswith(".pdf"):
        return "pdf", extract_from_pdf(file_bytes)
    if name.endswith(".pptx"):
        return "pptx", extract_from_pptx(file_bytes)
    # txt / md
    try:
        return "txt", file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        return "bin", ""
