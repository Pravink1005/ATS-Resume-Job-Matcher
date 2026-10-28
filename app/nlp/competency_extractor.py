import re

COMPETENCIES = [
    'communication', 'teamwork', 'collaboration', 'problem solving', 'problem-solving',
    'critical thinking', 'analytical thinking', 'attention to detail', 'decision making',
    'presentation', 'stakeholder management', 'cross-functional', 'adaptability',
    'leadership', 'time management'
]

def extract_competencies(text):
    if not isinstance(text, str) or not text.strip():
        return []
    low = text.lower()
    found = set()
    for c in COMPETENCIES:
        pattern = r'(?<!\w)' + re.escape(c) + r'(?!\w)'
        if re.search(pattern, low):
            found.add(c)
    return sorted(found)
