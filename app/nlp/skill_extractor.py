import re

SKILLS = [
    'python','sql','mysql','postgresql','postgres','mongodb','pandas','numpy','matplotlib','seaborn',
    'aws','azure','gcp','docker','jenkins','git','github','spark','pyspark','airflow','snowflake','kafka',
    'java','javascript','typescript','c++','c#','.net','linux','ubuntu','excel','power bi','tableau','looker',
    'scikit-learn','tensorflow','pytorch','streamlit','firebase','rest api','api','etl','data cleaning',
    'data validation','data quality','eda','data visualization','dashboard','reporting','cte','complex joins',
    'query optimization'
]

# Single-letter "r" is intentionally NOT a normal substring skill.
# It is accepted only when the resume clearly identifies R as a programming language/tool.
R_PATTERNS = [
    r'\br\s+(?:programming|language|studio)\b',
    r'\b(?:programming|coding|scripting)\s+in\s+r\b',
    r'\busing\s+r\b',
    r'\br\s*programming\b',
]


def _has_skill(text: str, skill: str) -> bool:
    return bool(re.search(r'(?<!\w)' + re.escape(skill) + r'(?!\w)', text))


def extract_skills(text: str):
    low = text.lower()
    found = {s for s in SKILLS if _has_skill(low, s)}
    if any(re.search(p, low) for p in R_PATTERNS):
        found.add('r')
    return sorted(found)
