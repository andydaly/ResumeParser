import re

SECTION_HEADERS = [
    r"education",
    r"experience|work history|employment",
    r"skills",
    r"projects",
    r"certifications",
    r"personal profile|summary|profile",
    r"achievements|awards",
    r"computer skills profile|technical skills profile|computer skills"
]
HEADER_RE = re.compile(rf"^\s*({'|'.join(SECTION_HEADERS)})\s*$", re.I | re.M)

def split_sections(text: str):
    sections = {}
    matches = list(HEADER_RE.finditer(text))
    if not matches:
        sections["body"] = text
        return sections
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[m.group(1).lower()] = text[start:end].strip()
    return sections
