import re
from app.core.exceptions import InvalidJobDescriptionException

class JobDescriptionParser:
    SKILL_TERMS = [
        # Languages & Core
        'python', 'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'java', 'javascript', 'typescript',
        'c++', 'c#', '.net', 'golang', 'kotlin', 'swift', 'scala',
        # Data & Analytics
        'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'excel', 'power bi', 'tableau', 'looker',
        'etl', 'data cleaning', 'data validation', 'data quality', 'eda', 'data visualization', 'dashboard',
        'reporting', 'cte', 'complex joins', 'query optimization', 'dbt', 'bigquery', 'snowflake', 'redshift',
        # Big Data & Streaming
        'spark', 'pyspark', 'airflow', 'kafka', 'hadoop',
        # AI & ML
        'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'machine learning', 'deep learning', 'nlp',
        'llm', 'langchain', 'huggingface', 'opencv',
        # Web & Frameworks
        'react', 'next.js', 'vue', 'angular', 'node.js', 'fastapi', 'django', 'flask', 'spring boot',
        'graphql', 'rest api', 'api', 'microservices', 'html', 'css', 'tailwind', 'streamlit',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd',
        'terraform', 'ansible', 'linux', 'ubuntu', 'firebase', 'redis', 'elasticsearch', 'r', 'go'
    ]

    def parse(self, job_description):
        if not isinstance(job_description, str):
            raise TypeError('Job description must be a string.')
        if not job_description.strip():
            raise InvalidJobDescriptionException('Job description cannot be empty.')
        text = job_description.strip()
        return {
            'job_title': self._title(text),
            'skills': self._skills(text),
            'required_experience': self._experience(text),
            'education': self._education(text),
            'location': self._location(text),
            'work_authorization': self._work_authorization(text),
            'description': text,
        }

    def _title(self, text):
        m = re.search(r'(?im)^\s*(?:job title|role|position)\s*:\s*(.+)$', text)
        if m:
            return m.group(1).strip()
        return text.splitlines()[0].strip()[:150] if text.splitlines() else 'Unknown Role'

    def _skills(self, text):
        low = text.lower()
        found = set()
        for x in self.SKILL_TERMS:
            if x == 'r':
                if re.search(r'\br\s+(?:programming|language|studio)\b|\busing\s+r\b|\bprogramming\s+in\s+r\b', low):
                    found.add(x)
            elif x == 'go':
                if re.search(r'\bgo\s+(?:programming|language)\b|\bprogramming\s+in\s+go\b|\bgolang\b', low):
                    found.add(x)
            elif re.search(r'(?<!\w)' + re.escape(x) + r'(?!\w)', low):
                found.add(x)
        return sorted(found)

    def _experience(self, text):
        patterns = [
            r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience',
            r'(?:experience|exp)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b'
        ]
        vals = [float(m.group(1)) for p in patterns for m in re.finditer(p, text, re.I)]
        return max(vals) if vals else 0.0

    def _education(self, text):
        low = text.lower()
        return [x for x in [
            'bachelor','b.sc','b.tech','b.e','bca','master','m.sc','m.tech','m.e','mca','mba',
            'computer science','statistics','mathematics','economics','information systems',
            'information technology','data science','business analytics','business analysis'
        ] if x in low]

    def _location(self, text):
        low = text.lower()
        if re.search(r'\b(remote|work from home|fully remote)\b', low):
            return 'remote'
        m = re.search(r'\b(?:location|located in|based in)\s*[:\-]?\s*([a-z][^.!?\n]{1,60})', text, re.I)
        return m.group(1).strip(' .,').lower() if m else None

    def _work_authorization(self, text):
        low = text.lower()
        if re.search(r'no\s+(?:visa\s+)?sponsorship|without\s+sponsorship|must\s+be\s+authorized', low):
            return 'authorized_without_sponsorship'
        if re.search(r'sponsorship\s+(?:is\s+)?(?:available|provided)', low):
            return 'sponsorship_available'
        if re.search(r'authorized\s+to\s+work|work\s+authorization|legally\s+authorized|right\s+to\s+work|visa\s+sponsorship', low):
            return 'authorization_required'
        return None
