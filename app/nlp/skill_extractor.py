import re

SKILLS = [
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
    'aws', 'azure', 'gcp', 'oci', 'oke', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd',
    'terraform', 'ansible', 'linux', 'ubuntu', 'firebase', 'redis', 'elasticsearch',
    'grafana', 'prometheus', 'opentelemetry', 'datadog', 'splunk', 'sre', 'devops', 'containers',
    # Enterprise Security & Identity
    'microsoft purview', 'purview', 'zscaler', 'iam'
]

# Single-letter "r" is intentionally NOT a normal substring skill.
# It is accepted only when the resume clearly identifies R as a programming language/tool.
R_PATTERNS = [
    r'\br\s+(?:programming|language|studio)\b',
    r'\b(?:programming|coding|scripting)\s+in\s+r\b',
    r'\busing\s+r\b',
    r'\br\s*programming\b',
]

GO_PATTERNS = [
    r'\bgo\s+(?:programming|language)\b',
    r'\b(?:programming|coding)\s+in\s+go\b',
    r'\bgolang\b',
]


def _has_skill(text: str, skill: str) -> bool:
    return bool(re.search(r'(?<!\w)' + re.escape(skill) + r'(?!\w)', text))


def extract_skills(text: str):
    low = text.lower()
    found = {s for s in SKILLS if _has_skill(low, s)}
    if any(re.search(p, low) for p in R_PATTERNS):
        found.add('r')
    if any(re.search(p, low) for p in GO_PATTERNS):
        found.add('go')
    return sorted(found)
