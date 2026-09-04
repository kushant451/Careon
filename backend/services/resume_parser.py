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

def _iter_block_items(parent):
    """
    Yield paragraphs and tables in the order they appear in the document
    body (or inside a table cell). doc.paragraphs / doc.tables alone miss
    content, or lose ordering, for templates that mix the two — e.g. a
    sidebar + main-content layout built with Word tables.
    """
    from docx.document import Document as _Document
    from docx.table import _Cell, Table
    from docx.text.paragraph import Paragraph
    from docx.oxml.ns import qn

    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("Unsupported parent type")

    for child in parent_elm.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def _extract_docx_text(parent):
    """Recursively pull text from paragraphs and table cells (tables can
    be nested inside other table cells, e.g. a sidebar layout)."""
    from docx.table import Table

    lines = []
    for block in _iter_block_items(parent):
        if isinstance(block, Table):
            for row in block.rows:
                for cell in row.cells:
                    lines.extend(_extract_docx_text(cell))
        else:
            text = block.text.strip()
            if text:
                lines.append(text)
    return lines


def _from_docx(filepath):
    doc = python_docx.Document(filepath)
    lines = _extract_docx_text(doc)

    # Fallback safety net: some templates put content in headers/footers,
    # or nest tables in ways that trip up the walk above — grab any
    # remaining paragraph/table text so we don't reject a real resume.
    if not lines:
        for p in doc.paragraphs:
            if p.text.strip():
                lines.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        if p.text.strip():
                            lines.append(p.text.strip())

    if not lines:
        raise ValueError(
            "Could not extract text from this DOCX. If it contains text "
            "boxes or images, please upload it as a PDF instead."
        )
    return clean("\n".join(lines))