import re
from typing import List, Dict, Optional

DASH = r"[-\u2013\u2014]"
SPLIT_RE = re.compile(rf"\s*{DASH}\s*")

YEAR_AT_START_RE = re.compile(r"^\s*(\d{4})\b")
YEAR_RANGE_RE = re.compile(rf"^\s*(?P<start>\d{{4}})\s*(?:{DASH}|/|to)\s*(?P<end>\d{{4}})\b", re.I)

RESULT_HINT_RE = re.compile(
    r"""
    \b(
        (bsc|ba|msc|ma|phd|b\.?eng|m\.?eng|b\.?tech|m\.?tech)  # degrees
        |honours?|hons|first\s+class|second\s+class|2\.?1|2\.?2|distinction|merit|gpa
        |major\s+award|certificate|cert|diploma|higher\s+diploma|hnd|scqf
    )\b
    """,
    re.I | re.VERBOSE,
)

INSTITUTION_HINT_RE = re.compile(
    r"\b(univ|university|college|institute|institut|school|centre|center|polytechnic|academy|dit|it|dit,)\b",
    re.I,
)

def _extract_year(line: str) -> (Optional[str], str):
    m = YEAR_RANGE_RE.match(line)
    if m:
        year = m.group("end")
        rest = line[m.end():].lstrip(" -\u2013\u2014")
        return year, rest
    m2 = YEAR_AT_START_RE.match(line)
    if m2:
        year = m2.group(1)
        rest = line[m2.end():].lstrip(" -\u2013\u2014")
        return year, rest
    return None, line

def _classify_segments(segments: List[str]) -> Dict[str, Optional[str]]:
    parts = [s.strip() for s in segments if s.strip()]
    out = {"course": None, "result": None, "institution": None}
    if not parts:
        return out

    out["course"] = parts[0]

    if len(parts) == 1:
        return out

    if len(parts) == 2:
        p1 = parts[1]
        if RESULT_HINT_RE.search(p1) and not INSTITUTION_HINT_RE.search(p1):
            out["result"] = p1
        else:
            out["institution"] = p1
        return out

    tail = parts[1:]
    result_idx = None
    for idx, seg in enumerate(tail):
        if RESULT_HINT_RE.search(seg):
            result_idx = idx
            break

    if result_idx is not None:
        out["result"] = tail[result_idx]
        inst_parts = tail[:result_idx] + tail[result_idx + 1 :]
        out["institution"] = " - ".join(inst_parts) if inst_parts else None
    else:
        out["institution"] = " - ".join(tail)

    return out

def parse_education_section(section_text: str) -> List[Dict]:
    records: List[Dict] = []
    for raw in section_text.splitlines():
        line = raw.strip()
        if not line:
            continue

        if line.lower().startswith(("education", "achievements", "awards", "work history", "experience")):
            continue

        year, rest = _extract_year(line)
        if not year:
            continue

        segs = SPLIT_RE.split(rest)
        fields = _classify_segments(segs)

        records.append({
            "graduation_date": year,
            "course": fields["course"],
            "result": fields["result"],
            "institution": fields["institution"],
        })
    return records