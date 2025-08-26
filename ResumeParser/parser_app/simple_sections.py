import re
from typing import List, Optional, Dict, Iterable

BULLET_RE = re.compile(
    r"^\s*(?:[\u2022\u2023\u25E6\u002D\u2013\u2014\*]+|(?:\d+[\.\)])\s+)\s*(.*\S)\s*$"
)

STOP_HDR_RE = re.compile(
    r"\s*(achievements?|awards?|work history|experience|education|skills?|computer skills profile|technical skills profile|computer skills)\s*",
    re.I,
)

def get_section_text(sections: Dict[str, str], candidates: Iterable[str]) -> Optional[str]:
    if not sections:
        return None
    clist = [c.lower() for c in candidates]
    for k, v in sections.items():
        kl = k.lower()
        if any(c in kl for c in clist):
            return v
    return None


def extract_profile(sections: Dict[str, str], raw_text: str) -> Optional[str]:
    if not sections:
        return None
    ranked: List[tuple[int, str]] = []
    for k, v in sections.items():
        kl = k.lower().strip()
        if "personal profile" in kl:
            ranked.append((0, v))
        elif kl == "summary" or "summary" in kl:
            ranked.append((1, v))
        elif "profile" in kl:
            ranked.append((2, v))
    if not ranked:
        return None
    ranked.sort(key=lambda x: x[0])
    text = ranked[0][1].strip()

    out_lines = []
    for ln in text.splitlines():
        if STOP_HDR_RE.fullmatch(ln):
            break
        if ln.strip():
            out_lines.append(ln.strip())
    return "\n".join(out_lines) or None

def parse_achievements(section_text: Optional[str]) -> List[str]:
    if not section_text:
        return []

    lines = [ln.rstrip() for ln in section_text.splitlines()]

    has_bullets = any(BULLET_RE.match(ln.strip()) for ln in lines)

    def is_header(ln: str) -> bool:
        return bool(re.fullmatch(r"(achievements?|awards?)", ln.strip(), re.I))

    cleaned = [ln for ln in lines if ln.strip() and not is_header(ln)]

    if not cleaned:
        return []

    if not has_bullets:
        return [ln.strip() for ln in cleaned if ln.strip()]

    items: List[str] = []
    cur: List[str] = []

    def flush():
        nonlocal cur
        if cur:
            s = " ".join(part.strip() for part in cur if part.strip())
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                items.append(s)
            cur = []

    for raw in cleaned:
        ln = raw.strip()
        m = BULLET_RE.match(ln)
        if m:
            flush()
            cur = [m.group(1).strip()]
        else:
            if cur:
                cur.append(ln)
            else:
                cur = [ln]
    flush()

    return items


def parse_skills_profile(section_text: str) -> Optional[str]:
    section_text = section_text.strip()
    return section_text or None
