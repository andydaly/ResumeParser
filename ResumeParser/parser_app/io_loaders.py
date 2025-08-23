from pathlib import Path
import pdfplumber
import docx

def load_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        pages = []
        with pdfplumber.open(p) as pdf:
            for pg in pdf.pages:
                pages.append(pg.extract_text() or "")
        return "\n".join(pages)
    if p.suffix.lower() == ".docx":
        d = docx.Document(p)
        return "\n".join(para.text for para in d.paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")
