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
    re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:hands[- ]on\s+|professional\s+|relevant\s+|industry\s+|work\s+|total\s+|overall\s+|practical\s+)?experience", re.I),
    re.compile(r"(?:experience|exp)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", re.I),
    re.compile(r"(?:over|around|about|nearly)\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:hands[- ]on\s+|professional\s+|relevant\s+|industry\s+|work\s+)?experience", re.I),
]

_DATE_PATTERNS = [
    # Numeric format: 07/2025 – 07/2026, 07-2025 to 07-2026, 07.2025 - Present
    re.compile(r"(?P<sm>\d{1,2})[/\.-](?P<sy>19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(?:(?P<em>\d{1,2})[/\.-](?P<ey>19\d{2}|20\d{2})|(?P<present>present|current|now|till\s+date))", re.I),
    # Named month format: Jul 2025 – Jul 2026, July 2025 to Present
    re.compile(r"(?P<sm>[A-Za-z]{3,9})\.?\s+(?P<sy>19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(?:(?P<em>[A-Za-z]{3,9})\.?\s+(?P<ey>19\d{2}|20\d{2})|(?P<present>present|current|now|till\s+date))", re.I),
    # Named month with slash: Jul/2025 - Jul/2026
    re.compile(r"(?P<sm>[A-Za-z]{3,9})\.?[/\.-](?P<sy>19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(?:(?P<em>[A-Za-z]{3,9})\.?[/\.-](?P<ey>19\d{2}|20\d{2})|(?P<present>present|current|now|till\s+date))", re.I),
]


def _parse_month(val: str | None) -> int | None:
    if not val:
        return None
    val = val.strip().lower()
    if val.isdigit():
        m = int(val)
        return m if 1 <= m <= 12 else None
    return MONTHS.get(val[:3]) or MONTHS.get(val)


def _section(text: str) -> str:
    lines = text.replace("\r", "\n").split("\n")
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        low = line.strip().lower()
        words = line.strip().split()
        # Header must be at the start of a line and be a short title line (<= 5 words)
        if start is None and re.search(r"^\s*(?:professional\s+|work\s+|relevant\s+|employment\s+)?experience\b|^\s*employment\s+(?:history|record)\b", low) and len(words) <= 5:
            start = i
            continue
        if start is not None and re.search(r"^\s*(?:projects?|education|academic|technical\s+skills|skills|certifications?|activities|declaration|achievements?|awards?)\b", low) and len(words) <= 5:
            end = i
            break
    return "\n".join(lines[start:end]) if start is not None else text


def extract_experience(text: str) -> float:
    if not isinstance(text, str) or not text.strip():
        return 0.0

    explicit = []
    for pattern in _EXPLICIT:
        explicit.extend(float(m.group(1)) for m in pattern.finditer(text))
    max_explicit = max(explicit) if explicit else 0.0

    section = _section(text)
    today = date.today()

    intervals = []
    seen_spans = []
    for p in _DATE_PATTERNS:
        for m in p.finditer(section):
            span = m.span()
            if any(s[0] <= span[0] and span[1] <= s[1] for s in seen_spans):
                continue
            seen_spans.append(span)

            sm = _parse_month(m.group("sm"))
            sy = int(m.group("sy"))
            if m.group("present"):
                ey, em = today.year, today.month
            else:
                em = _parse_month(m.group("em"))
                ey = int(m.group("ey")) if m.group("ey") else None
            if not sm or not sy or not em or not ey:
                continue

            start_month_idx = sy * 12 + sm
            end_month_idx = ey * 12 + em
            if end_month_idx >= start_month_idx:
                intervals.append((start_month_idx, end_month_idx))

    # Merge overlapping intervals to prevent double-counting concurrent roles
    if intervals:
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for current in intervals[1:]:
            prev_start, prev_end = merged[-1]
            if current[0] <= prev_end:
                merged[-1] = (prev_start, max(prev_end, current[1]))
            else:
                merged.append(current)
        total_months = sum((end - start + 1) for start, end in merged)
        date_years = round(total_months / 12.0, 2)
    else:
        date_years = 0.0

    return max(max_explicit, date_years)

