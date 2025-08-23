import re
from pathlib import Path
import phonenumbers
import spacy
from rapidfuzz import fuzz, process as rfprocess

_nlp = spacy.load("en_core_web_sm")

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
URL_RE   = re.compile(r"https?://\S+|www\.\S+", re.I)
PUNCT_LINE_RE = re.compile(r"^[-–•·]+$")

def _get_contact_block(text: str, lines: int = 10) -> str:
    head = "\n".join(text.splitlines()[:lines])
    head = URL_RE.sub("", head)
    return "\n".join(
        ln.strip()
        for ln in head.splitlines()
        if ln.strip() and not PUNCT_LINE_RE.fullmatch(ln.strip())
    )

def extract_email(text: str):
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None

def extract_phone(text: str, default_region: str = "GB"):
    best = None
    for m in phonenumbers.PhoneNumberMatcher(text, default_region):
        formatted = phonenumbers.format_number(m.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        if formatted.startswith("+"):
            return formatted
        best = best or formatted
    return best

def guess_name(text: str):
    head = _get_contact_block(text)
    doc = _nlp(head)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            candidate = ent.text.strip()
            if "@" in candidate or any(ch.isdigit() for ch in candidate):
                continue
            tokens = candidate.split()
            if 1 < len(tokens) <= 4 and all(tok.isalpha() for tok in tokens):
                return candidate


    for ln in head.splitlines():
        if EMAIL_RE.search(ln):
            continue
        if any(ch.isdigit() for ch in ln):
            continue
        if URL_RE.search(ln):
            continue
        parts = ln.strip().split()
        if 1 < len(parts) <= 4:
            return ln.strip()

    return None


def load_skill_list(path: str):
    return [
        s.strip()
        for s in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
        if s.strip()
    ]

def extract_skills(text: str, skills_vocab: list[str], limit=100):
    results = rfprocess.extract(
        text, skills_vocab, scorer=fuzz.partial_ratio, processor=lambda s: s.lower(), limit=limit
    )
    return sorted({s for s, score, _ in results if score >= 90})

def _clean_url(u: str) -> str:
    u = u.strip().strip(")];,.")
    if u.lower().startswith("www."):
        u = "https://" + u
    return u

def extract_github_url(text: str) -> str | None:

    gh_re = re.compile(r"(https?://|www\.)?github\.com/[A-Za-z0-9_.-]+(?:/?|[^\s)]*)", re.I)
    m = gh_re.search(text)
    return _clean_url(m.group(0)) if m else None

def extract_linkedin_url(text: str) -> str | None:

    li_re = re.compile(r"(https?://|www\.)?linkedin\.com/(in|pub|profile)/[A-Za-z0-9._%+-/]+", re.I)
    m = li_re.search(text)
    if m:
        return _clean_url(m.group(0))

    any_li = re.compile(r"(https?://|www\.)?linkedin\.com/\S+", re.I)
    m2 = any_li.search(text)
    return _clean_url(m2.group(0)) if m2 else None