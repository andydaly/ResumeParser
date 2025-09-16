from __future__ import annotations
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass
import dateparser

DASH = r"[-\u2013\u2014]"

MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t\.?|tember)|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
NUM_MONTH = r"(?:1[0-2]|0?[1-9])"

DATE_TOKEN = rf"(?:{MONTHS}\s+\d{{4}}|\d{{4}}/{NUM_MONTH}|{NUM_MONTH}/\d{{4}}|\d{{4}})"
DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:{DASH}|to)\s*(?P<end>{DATE_TOKEN}|present|current|now)",
    re.I,
)

YEAR_AT_START_RE = re.compile(r"^\s*\d{4}\b")
SPLIT_LAST_DASH_RE = re.compile(rf"\s{DASH}\s")

BULLET_RE = re.compile(rf"^\s*(?:[\u2022\u2023\u25E6\*{DASH}]+)\s+(.*\S)\s*$")

HEADER_SPLIT_RE = re.compile(rf"\s*(?:{DASH}|\sat\s|\s@\s)\s*", re.I)

SEPARATOR_LINE_RE = re.compile(r"^\s*[•\-\u2013\u2014·\.]{2,}\s*$")

LIKELY_TITLE_TOKENS = {
    "engineer","developer","programmer","lead","senior","principal",
    "architect","manager","consultant","intern","analyst","administrator",
    "director","specialist","freelance"
}

@dataclass
class ExperienceItem:
    title: Optional[str]
    company: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description_lines: List[str]

def _norm_date(token: str | None) -> Optional[str]:
    if not token:
        return None
    token = token.strip().lower().replace("—", "-").replace("–", "-")
    if token in ("present", "current", "now"):
        return "Present"
    dt = dateparser.parse(
        token,
        settings={"PREFER_DAY_OF_MONTH": "first", "PREFER_DATES_FROM": "past"},
    )
    if not dt:
        return None

    return dt.strftime("%Y-%m")

def _looks_like_title(s: str) -> bool:
    low = s.lower()
    return any(tok in low for tok in LIKELY_TITLE_TOKENS)

def _split_header_guess_title_company(header: str) -> Tuple[Optional[str], Optional[str]]:
    s = header.strip()

    m = DATE_RANGE_RE.match(s)
    if m:
        s = s[m.end():]
        s = re.sub(rf"^\s*{DASH}\s*", "", s) 

    m_at = re.search(r"\s(?:at|@)\s(.+)$", s, re.I)
    if m_at:
        before = s[:m_at.start()].strip(" -\u2013\u2014")
        company = m_at.group(1).strip(" -\u2013\u2014")
        title = before or None
        if company and _looks_like_title(company):
            return (s.strip(" -\u2013\u2014") or None, None)
        return (title, company or None)

    parts = SPLIT_LAST_DASH_RE.split(s)
    if len(parts) >= 2:
        title = " - ".join(parts[:-1]).strip(" -\u2013\u2014")
        company = parts[-1].strip(" -\u2013\u2014")
        if company and _looks_like_title(company):
            return (s.strip(" -\u2013\u2014") or None, None)
        return (title or None, company or None)

    return (s.strip(" -\u2013\u2014") or None, None)

def _looks_like_header(line: str) -> bool:
    if SEPARATOR_LINE_RE.match(line) or not line.strip():
        return False
    if DATE_RANGE_RE.search(line):
        return True
    if YEAR_AT_START_RE.search(line) and HEADER_SPLIT_RE.search(line):
        return True
    return False

def _collect_description(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    desc: List[str] = []
    i = start_idx
    while i < len(lines):
        raw = lines[i].rstrip()
        if _looks_like_header(raw):
            break
        if not raw.strip():
            if desc and desc[-1] != "":
                desc.append("")
            i += 1
            continue
        m = BULLET_RE.match(raw)
        if m:
            desc.append(m.group(1).strip())
        else:
            desc.append(raw.strip())
        i += 1
    while desc and desc[-1] == "":
        desc.pop()
    return desc, i

def parse_experience_section(text: str) -> List[ExperienceItem]:
    lines = [ln.strip() for ln in text.splitlines()]
    i = 0
    items: List[ExperienceItem] = []
    while i < len(lines):
        line = lines[i]
        if not line or SEPARATOR_LINE_RE.match(line):
            i += 1
            continue

        if _looks_like_header(line):
            m = DATE_RANGE_RE.search(line)
            start = _norm_date(m.group("start")) if m else None
            end   = _norm_date(m.group("end")) if m else None
            title, company = _split_header_guess_title_company(line)

            i += 1
            desc, i = _collect_description(lines, i)

            items.append(ExperienceItem(
                title=title or None,
                company=company or None,
                start_date=start,
                end_date=end,
                description_lines=desc,
            ))
            continue

        i += 1

    return items

def parse_experience_from_whole_text(sections: dict[str, str] | None, raw_text: str) -> List[ExperienceItem]:
    if sections:
        for k, v in sections.items():
            key = k.lower()
            if "experience" in key or "work history" in key or "employment" in key:
                return parse_experience_section(v)
    return parse_experience_section(raw_text)
