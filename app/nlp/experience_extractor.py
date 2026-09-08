import re
from datetime import date

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6,
    "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9,
    "september": 9, "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_EXPLICIT = [
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", re.I),
    re.compile(r"(?:experience|exp)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.I),
]
_DATE_RANGE = re.compile(
    r"(?P<sm>[A-Za-z]{3,9})\s+(?P<sy>20\d{2})\s*(?:-|–|—|to)\s*(?:(?P<em>[A-Za-z]{3,9})\s+(?P<ey>20\d{2})|(?P<present>present|current))",
    re.I,
)


def _section(text: str) -> str:
    lines = text.replace("\r", "\n").split("\n")
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        low = line.strip().lower()
        if start is None and re.search(r"\b(work experience|professional experience|experience|employment)\b", low):
            start = i
            continue
        if start is not None and re.search(r"\b(education|skills|certifications|projects|achievements|summary|declaration)\b", low):
            end = i
            break
    return "\n".join(lines[start:end]) if start is not None else text


def _months_between(start_y, start_m, end_y, end_m):
    return max(0, (end_y - start_y) * 12 + (end_m - start_m))


def extract_experience(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0

    explicit = []
    for pattern in _EXPLICIT:
        explicit.extend(float(m.group(1)) for m in pattern.finditer(text))
    if explicit:
        return max(explicit)

    section = _section(text)
    today = date.today()
    months = 0
    for m in _DATE_RANGE.finditer(section):
        sm = MONTHS.get(m.group("sm").lower())
        if not sm:
            continue
        sy = int(m.group("sy"))
        if m.group("present"):
            ey, em = today.year, today.month
        else:
            em = MONTHS.get((m.group("em") or "").lower())
            ey = int(m.group("ey")) if m.group("ey") else None
        if not em or not ey:
            continue
        months += _months_between(sy, sm, ey, em)

    return round(months / 12.0, 2) if months else 0.0
