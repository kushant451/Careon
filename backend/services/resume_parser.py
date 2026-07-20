import pdfplumber
import docx as python_docx
from utils.text_cleaner import clean
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_text(filepath, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":   return _from_pdf(filepath)
    if ext == "docx":  return _from_docx(filepath)
    raise ValueError(f"Unsupported format: .{ext}")

def _from_pdf(filepath):
    parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: parts.append(t)
    if not parts:
        raise ValueError("Could not extract text. Use a text-based PDF, not a scanned image.")
    return clean("\n".join(parts))

def _from_docx(filepath):
    doc = python_docx.Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        raise ValueError("DOCX file appears empty.")
    return clean("\n".join(paragraphs))