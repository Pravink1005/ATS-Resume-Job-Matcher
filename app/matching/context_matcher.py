"""Evidence-based matching for title, seniority, location, and work authorization."""
import re


SENIORITY_LEVELS = {
    'intern': 0,
    'junior': 1,
    'entry': 1,
    'associate': 1,
    'mid': 2,
    'intermediate': 2,
    'senior': 3,
    'lead': 4,
    'principal': 5,
    'staff': 5,
    'manager': 4,
    'director': 6,
    'executive': 7,
}

AUTH_PATTERNS = [
    r'authorized\s+to\s+work', r'work\s+authorization', r'legally\s+authorized',
    r'right\s+to\s+work', r'visa\s+sponsorship', r'sponsorship\s+(?:is\s+)?(?:required|available|provided)',
]


def _normalized_words(value):
    return set(re.findall(r'[a-z0-9]+', (value or '').lower()))


def _seniority(value):
    low = (value or '').lower()
    for label, level in SENIORITY_LEVELS.items():
        if re.search(r'\b' + re.escape(label) + r'\b', low):
            return label, level
    return None, None


def _location(text):
    low = (text or '').lower()
    if re.search(r'\b(remote|work from home|fully remote)\b', low):
        return 'remote'
    match = re.search(r'\b(?:location|located in|based in)\s*[:\-]?\s*([a-z][^.!?\n]{1,60})', low, re.I)
    if match:
        return match.group(1).strip(' .,').lower()
    return None


def _authorization(text):
    low = (text or '').lower()
    found = [pattern for pattern in AUTH_PATTERNS if re.search(pattern, low)]
    if not found:
        return None
    if re.search(r'no\s+(?:visa\s+)?sponsorship|without\s+sponsorship|must\s+be\s+authorized', low):
        return 'authorized_without_sponsorship'
    if re.search(r'sponsorship\s+(?:is\s+)?(?:available|provided)', low):
        return 'sponsorship_available'
    return 'authorization_required'


def match_context(resume_text, job_title, job_text):
    resume_words = _normalized_words(resume_text)
    title_words = _normalized_words(job_title)
    title_overlap = len(title_words & resume_words) / len(title_words) if title_words else None

    job_seniority_label, job_seniority = _seniority(job_title + ' ' + job_text)
    resume_seniority_label, resume_seniority = _seniority(resume_text)
    if job_seniority is None:
        seniority_score = 100.0
    elif resume_seniority is None:
        seniority_score = 50.0
    elif resume_seniority >= job_seniority:
        seniority_score = 100.0
    elif resume_seniority == job_seniority - 1:
        seniority_score = 60.0
    else:
        seniority_score = 20.0

    resume_location = _location(resume_text)
    job_location = _location(job_text)
    if not job_location:
        location_score = 100.0
    elif job_location == 'remote':
        location_score = 100.0 if resume_location in {'remote', None} else 60.0
    elif not resume_location:
        location_score = 50.0
    elif job_location in resume_location or resume_location in job_location:
        location_score = 100.0
    else:
        location_score = 0.0

    resume_auth = _authorization(resume_text)
    job_auth = _authorization(job_text)
    if not job_auth:
        authorization_score = 100.0
    elif job_auth == 'sponsorship_available':
        authorization_score = 100.0
    elif resume_auth in {'authorization_required', 'authorized_without_sponsorship'}:
        authorization_score = 100.0
    else:
        authorization_score = 50.0

    return {
        'job_title': job_title,
        'title_match_score': round((title_overlap * 100) if title_overlap is not None else 100.0, 2),
        'job_seniority': job_seniority_label,
        'resume_seniority': resume_seniority_label,
        'seniority_score': seniority_score,
        'job_location': job_location,
        'resume_location': resume_location,
        'location_score': location_score,
        'job_authorization': job_auth,
        'resume_authorization': resume_auth,
        'authorization_score': authorization_score,
        'title_score': round((title_overlap * 100 if title_overlap is not None else 100.0) * .6 + seniority_score * .4, 2),
        'context_score': round((location_score + authorization_score) / 2, 2),
    }