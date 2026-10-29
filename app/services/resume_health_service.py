import re
from typing import Dict, Any, List


class ResumeHealthService:
    """Evaluates resume format, structure, and ATS parseability health."""

    STRONG_ACTION_VERBS = {
        'developed', 'engineered', 'architected', 'spearheaded', 'orchestrated',
        'optimized', 'implemented', 'designed', 'built', 'led', 'accelerated',
        'automated', 'streamlined', 'delivered', 'reduced', 'increased', 'scaled',
        'mentored', 'collaborated', 'created', 'deployed', 'monitored', 'managed',
        'configured', 'authored', 'established', 'formulated', 'pioneered',
        'transformed', 'analyzed', 'refactored', 'resolved', 'constructed',
        'integrated', 'standardized', 'boosted', 'saved', 'initiated', 'drove',
        'executed'
    }

    WEAK_PASSIVE_PHRASES = [
        'responsible for', 'duties included', 'helped with', 'worked on',
        'assisted in', 'was part of', 'participated in', 'helped to',
        'tasked with', 'worked with'
    ]

    SECTION_PATTERNS = {
        'experience': r'(?im)^\s*(?:work\s+|professional\s+|relevant\s+|employment\s+)?(?:experience|history)\b',
        'education': r'(?im)^\s*(?:education|academic\s+qualifications|academics|degrees?)\b',
        'skills': r'(?im)^\s*(?:technical\s+|core\s+)?(?:skills|technologies|proficiencies|tools|competencies)\b',
        'projects': r'(?im)^\s*(?:key\s+|personal\s+|academic\s+)?(?:projects|portfolio)\b',
        'certifications': r'(?im)^\s*(?:certifications?|licenses?|credentials?)\b',
        'summary': r'(?im)^\s*(?:professional\s+|career\s+)?(?:summary|profile|objective|about\s+me)\b',
    }

    def audit(self, text: str, filename: str = '') -> Dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            return {
                'health_score': 0,
                'grade': 'F',
                'contact_info': {},
                'sections_detected': [],
                'sections_missing': list(self.SECTION_PATTERNS.keys()),
                'metrics_found': [],
                'action_verbs_found': [],
                'weak_phrases_found': [],
                'word_count': 0,
                'page_estimate': 0.0,
                'score_breakdown': {},
                'checklist': {'critical': ['Resume contains no readable text.'], 'warnings': [], 'passed': []}
            }

        # 1. Contact Information
        contact = self._extract_contacts(text)

        # 2. Section Headers
        sections_detected = []
        sections_missing = []
        for sec_name, pattern in self.SECTION_PATTERNS.items():
            if re.search(pattern, text):
                sections_detected.append(sec_name)
            else:
                sections_missing.append(sec_name)

        # 3. Quantifiable Metrics & Numbers
        metrics_found = self._extract_metrics(text)

        # 4. Action Verbs & Passive Phrases
        action_verbs_found = self._extract_action_verbs(text)
        weak_phrases_found = self._extract_weak_phrases(text)

        # 5. Length & Formatting
        words = text.split()
        word_count = len(words)
        page_estimate = round(max(1.0, word_count / 450.0), 1)

        # 6. Score Calculation (0 - 100)
        breakdown = {}
        # Contact: max 25
        contact_pts = 0
        if contact.get('email'):
            contact_pts += 10
        if contact.get('phone'):
            contact_pts += 10
        if contact.get('linkedin') or contact.get('github') or contact.get('portfolio'):
            contact_pts += 5
        breakdown['contact_info'] = contact_pts

        # Structure / Sections: max 30
        struct_pts = 0
        if 'experience' in sections_detected:
            struct_pts += 10
        if 'education' in sections_detected:
            struct_pts += 10
        if 'skills' in sections_detected:
            struct_pts += 10
        breakdown['section_structure'] = struct_pts

        # Metrics & Impact: max 25
        metric_count = len(metrics_found)
        if metric_count >= 5:
            metric_pts = 25
        elif metric_count >= 3:
            metric_pts = 20
        elif metric_count >= 1:
            metric_pts = 12
        else:
            metric_pts = 0
        breakdown['quantifiable_metrics'] = metric_pts

        # Action Verbs & Active Voice: max 20
        verb_count = len(action_verbs_found)
        weak_count = len(weak_phrases_found)
        if verb_count >= 5 and weak_count == 0:
            verb_pts = 20
        elif verb_count >= 3 and weak_count <= 1:
            verb_pts = 16
        elif verb_count >= 1:
            verb_pts = max(5, 12 - (weak_count * 3))
        else:
            verb_pts = max(0, 8 - (weak_count * 4))
        breakdown['action_verb_strength'] = verb_pts

        total_score = min(100, max(0, sum(breakdown.values())))
        if total_score >= 85:
            grade = 'A'
        elif total_score >= 70:
            grade = 'B'
        elif total_score >= 55:
            grade = 'C'
        else:
            grade = 'D'

        # 7. Checklist (Critical, Warnings, Passed)
        checklist = {'critical': [], 'warnings': [], 'passed': []}

        # Contact checks
        if not contact.get('email'):
            checklist['critical'].append('No email address detected. Recruiters cannot reach you.')
        else:
            checklist['passed'].append(f"Email detected: {contact['email']}")

        if not contact.get('phone'):
            checklist['critical'].append('No phone number detected. An ATS parser may mark this profile incomplete.')
        else:
            checklist['passed'].append(f"Phone number detected: {contact['phone']}")

        if contact.get('linkedin'):
            checklist['passed'].append('LinkedIn profile link detected.')
        else:
            checklist['warnings'].append('No LinkedIn profile URL found. Including one increases recruiter credibility.')

        if contact.get('github'):
            checklist['passed'].append('GitHub / Portfolio link detected.')

        # Section checks
        if 'experience' not in sections_detected:
            checklist['critical'].append('No "Experience" section heading detected. ATS parsers may fail to categorize your career history.')
        else:
            checklist['passed'].append('Standard Experience section heading identified.')

        if 'education' not in sections_detected:
            checklist['warnings'].append('No "Education" section heading detected.')
        else:
            checklist['passed'].append('Standard Education section heading identified.')

        if 'skills' not in sections_detected:
            checklist['warnings'].append('No dedicated "Skills" section detected. A standalone skills block helps ATS keyword extraction.')
        else:
            checklist['passed'].append('Standard Skills section heading identified.')

        # Metrics checks
        if metric_count == 0:
            checklist['critical'].append('No quantifiable results found (e.g. %, $, numbers, scale). Resumes with measurable impact receive 40% more interview calls.')
        elif metric_count < 3:
            checklist['warnings'].append(f'Only {metric_count} quantifiable metric(s) found. Aim for at least 3-5 bullet points with numbers, percentages, or cost savings.')
        else:
            checklist['passed'].append(f'{metric_count} quantifiable metrics detected with measurable business impact.')

        # Action verbs check
        if weak_phrases_found:
            checklist['warnings'].append(f'Passive phrases detected: {", ".join(weak_phrases_found[:3])}. Replace with strong action verbs (e.g., "Engineered", "Orchestrated", "Delivered").')
        if verb_count >= 4:
            checklist['passed'].append(f'{verb_count} strong action verbs used across experience bullet points.')
        else:
            checklist['warnings'].append('Few strong action verbs identified. Begin bullet points with dynamic verbs.')

        # Length check
        if word_count < 60:
            checklist['critical'].append(f'Resume is extremely short ({word_count} words). May be missing career details or failed OCR.')
        elif word_count < 150:
            checklist['warnings'].append(f'Resume is relatively brief ({word_count} words). Consider detailing more projects and achievements.')
        elif word_count > 1500:
            checklist['warnings'].append(f'Resume is long ({word_count} words, ~{page_estimate} pages). Keep it concise and focused on high-priority achievements.')
        else:
            checklist['passed'].append(f'Healthy resume length ({word_count} words, ~{page_estimate} page(s)).')

        return {
            'health_score': total_score,
            'grade': grade,
            'contact_info': contact,
            'sections_detected': sections_detected,
            'sections_missing': sections_missing,
            'metrics_found': metrics_found[:10],
            'action_verbs_found': action_verbs_found[:15],
            'weak_phrases_found': weak_phrases_found[:10],
            'word_count': word_count,
            'page_estimate': page_estimate,
            'score_breakdown': breakdown,
            'checklist': checklist
        }

    def _extract_contacts(self, text: str) -> Dict[str, str]:
        contacts = {}
        # Email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
        if email_match:
            contacts['email'] = email_match.group(0)

        # Phone
        phone_match = re.search(
            r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b)',
            text
        )
        if phone_match:
            contacts['phone'] = phone_match.group(0).strip()

        # LinkedIn
        li_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|profile)\/[\w\-_]+', text, re.I)
        if not li_match:
            li_match = re.search(r'\blinkedin\.com\/[^\s,]+\b', text, re.I)
        if li_match:
            contacts['linkedin'] = li_match.group(0).rstrip('.,')

        # GitHub
        gh_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[\w\-_]+', text, re.I)
        if gh_match:
            contacts['github'] = gh_match.group(0).rstrip('.,')

        # Portfolio / Personal Website
        pf_match = re.search(r'(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+\.(?:io|dev|me|portfolio|site)(?:\/[^\s,]*)?', text, re.I)
        if pf_match and 'linkedin' not in pf_match.group(0).lower() and 'github' not in pf_match.group(0).lower():
            contacts['portfolio'] = pf_match.group(0).rstrip('.,')

        return contacts

    def _extract_metrics(self, text: str) -> List[str]:
        metrics = []
        patterns = [
            r'\b\d+(?:\.\d+)?%',
            r'[\$€£₹]\s*\d+(?:,\d{3})*(?:\.\d+)?(?:\s*[kmbtKMBT](?:illion)?)?',
            r'\b\d+(?:,\d{3})*\+?\s*(?:k|m|b|million|billion|users|customers|clients|requests|qps|ms|seconds|teams|engineers|projects|datasets|records|hours|days|weeks)\b',
            r'\b\d+x\s+(?:faster|more|higher|growth)\b',
            r'\b(?:reduced|increased|improved|saved|scaled)\s+(?:by\s+)?\d+(?:\.\d+)?%?',
        ]
        seen = set()
        for p in patterns:
            for m in re.finditer(p, text, re.I):
                val = m.group(0).strip()
                if val.lower() not in seen:
                    metrics.append(val)
                    seen.add(val.lower())
        return metrics

    def _extract_action_verbs(self, text: str) -> List[str]:
        low = text.lower()
        found = []
        for verb in self.STRONG_ACTION_VERBS:
            if re.search(r'(?<!\w)' + re.escape(verb) + r'(?!\w)', low):
                found.append(verb)
        return sorted(found)

    def _extract_weak_phrases(self, text: str) -> List[str]:
        low = text.lower()
        found = []
        for phrase in self.WEAK_PASSIVE_PHRASES:
            if phrase in low:
                found.append(phrase)
        return found
