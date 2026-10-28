"""Rule-based job requirement extraction for evidence-based ATS scoring.

The extractor intentionally stays conservative: a requirement is only created when
we can identify a meaningful skill, competency, education, experience, or
responsibility concept in the job description.
"""
import re
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class Requirement:
    name: str
    canonical: str
    category: str
    required: bool
    proficiency: str | None = None
    alternative_group: str | None = None
    source: str = ""

    def to_dict(self):
        return asdict(self)


SKILL_PATTERNS = [
    # Data Analysis & BI
    ("advanced sql", "advanced sql"), ("complex joins", "complex joins"),
    ("ctes", "cte"), ("cte", "cte"), ("query optimization", "query optimization"),
    ("advanced excel", "advanced excel"), ("excel", "excel"),
    ("power bi", "power bi"), ("microsoft power bi", "power bi"),
    ("tableau", "tableau"), ("looker", "looker"),
    # Programming Languages
    ("python", "python"), ("java", "java"), ("javascript", "javascript"),
    ("typescript", "typescript"), ("c++", "c++"), ("c#", "c#"), (".net", ".net"),
    ("go", "go"), ("golang", "go"), ("go programming", "go"), ("go language", "go"),
    ("r programming", "r"), ("r language", "r"), ("kotlin", "kotlin"), ("swift", "swift"),
    # Frontend
    ("react", "react"), ("react.js", "react"), ("reactjs", "react"),
    ("next.js", "next.js"), ("nextjs", "next.js"),
    ("vue", "vue"), ("vue.js", "vue"), ("vuejs", "vue"),
    ("angular", "angular"), ("angularjs", "angular"),
    ("html", "html"), ("css", "css"), ("tailwind", "tailwind"),
    # Backend & Frameworks
    ("fastapi", "fastapi"), ("django", "django"), ("flask", "flask"),
    ("spring boot", "spring boot"), ("springboot", "spring boot"),
    ("node.js", "node.js"), ("nodejs", "node.js"),
    ("graphql", "graphql"), ("rest api", "rest api"), ("restful api", "rest api"),
    ("microservices", "microservices"),
    # Databases & Caching
    ("sql", "sql"), ("mysql", "mysql"), ("postgresql", "postgresql"), ("postgres", "postgresql"),
    ("mongodb", "mongodb"), ("redis", "redis"), ("elasticsearch", "elasticsearch"),
    ("snowflake", "snowflake"), ("bigquery", "bigquery"), ("redshift", "redshift"),
    # Cloud & DevOps
    ("aws", "aws"), ("azure", "azure"), ("gcp", "gcp"),
    ("docker", "docker"), ("kubernetes", "kubernetes"), ("k8s", "kubernetes"),
    ("jenkins", "jenkins"), ("git", "git"), ("github", "github"), ("gitlab", "gitlab"),
    ("terraform", "terraform"), ("ansible", "ansible"), ("ci/cd", "ci/cd"),
    ("linux", "linux"),
    # Big Data & Data Eng
    ("spark", "spark"), ("pyspark", "pyspark"), ("airflow", "airflow"),
    ("kafka", "kafka"), ("dbt", "dbt"), ("etl", "etl"),
    # Machine Learning & AI
    ("machine learning", "machine learning"), ("deep learning", "deep learning"),
    ("nlp", "nlp"), ("natural language processing", "nlp"),
    ("llm", "llm"), ("large language models", "llm"), ("langchain", "langchain"),
    ("scikit-learn", "scikit-learn"), ("tensorflow", "tensorflow"), ("pytorch", "pytorch"),
    ("pandas", "pandas"), ("numpy", "numpy"),
]

CONCEPT_PATTERNS = [
    ("data extraction", "data extraction"), ("data cleaning", "data cleaning"),
    ("data cleansing", "data cleaning"), ("reporting", "reporting"),
    ("dashboard design", "dashboard design"), ("dashboards", "dashboard"),
    ("trend analysis", "trend analysis"), ("exploratory data analysis", "eda"),
    ("eda", "eda"), ("key performance indicators", "kpi"), ("kpis", "kpi"),
    ("data governance", "data governance"), ("actionable insights", "actionable insights"),
    ("business insights", "business insights"), ("cross-functional", "cross-functional"),
    ("stakeholder", "stakeholder management"), ("communication", "communication"),
    ("code review", "code review"), ("system design", "system design"),
    ("agile", "agile"), ("scrum", "scrum"), ("ci/cd pipeline", "ci/cd"),
    ("data pipeline", "data pipeline"), ("data modeling", "data modeling"),
    ("problem solving", "problem solving"), ("team player", "collaboration"),
    ("collaboration", "collaboration"), ("leadership", "leadership"),
]


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def _required(sentence: str) -> bool:
    low = sentence.lower()
    # Preferred/bonus wording should not be treated as a mandatory requirement.
    if re.search(r"\b(preferred|nice to have|bonus|plus|desirable|optional)\b", low):
        return False
    return True


def _proficiency(sentence: str, name: str):
    low = sentence.lower()
    if "advanced" in low:
        return "advanced"
    if "expert" in low:
        return "expert"
    if "intermediate" in low:
        return "intermediate"
    if "basic" in low:
        return "basic"
    return None


def extract_requirements(text: str):
    if not isinstance(text, str) or not text.strip():
        return []

    requirements = []
    seen = set()
    sentences = _sentences(text)

    for sentence in sentences:
        low = sentence.lower()
        required = _required(sentence)
        # An "or" list is an alternative group: one successful option should satisfy the group.
        alt_group = None
        if re.search(r"\bor\b", low) and any(x in low for x, _ in SKILL_PATTERNS):
            alt_group = "alt_" + hashlib.sha1(sentence.encode("utf-8")).hexdigest()[:10]

        suppressed = set()
        if re.search(r"\badvanced\s+sql\b", low):
            suppressed.add("sql")
        if re.search(r"\badvanced\s+excel\b", low):
            suppressed.add("excel")

        for display, canonical in SKILL_PATTERNS:
            if display in ("r programming", "r language"):
                matched = bool(re.search(r"\br\s+(?:programming|language|studio)\b", low))
            elif display in ("go", "go programming", "go language"):
                matched = bool(re.search(r"\bgo\s+(?:programming|language|developer|engineer)\b|\bgolang\b|(?:^|[,/|•\n:])\s*go\s*(?:[,/|•\n]|$)", low))
            else:
                matched = bool(re.search(r"(?<!\w)" + re.escape(display) + r"(?!\w)", low))
            if matched and canonical not in suppressed and canonical not in seen:
                req = Requirement(
                    name=display,
                    canonical=canonical,
                    category="technical_skill",
                    required=required,
                    proficiency=_proficiency(sentence, display),
                    alternative_group=alt_group,
                    source=sentence,
                )
                requirements.append(req)
                seen.add(canonical)

        for display, canonical in CONCEPT_PATTERNS:
            if re.search(r"(?<!\w)" + re.escape(display) + r"(?!\w)", low) and canonical not in seen:
                requirements.append(Requirement(
                    name=display,
                    canonical=canonical,
                    category="responsibility" if canonical not in {
                        "communication", "cross-functional", "stakeholder management",
                        "problem solving", "collaboration", "leadership"
                    } else "competency",
                    required=required,
                    proficiency=None,
                    alternative_group=None,
                    source=sentence,
                ))
                seen.add(canonical)

    # Education and experience are kept as separate structured requirements.
    exp = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?(?:data|analytics|bi|relevant|work)?\s*experience", text, re.I)
    if not exp:
        exp = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b", text, re.I)
    if exp:
        sentence = next((s for s in sentences if exp.group(0).lower() in s.lower()), exp.group(0))
        requirements.append(Requirement(
            name=f"{exp.group(1)}+ years experience",
            canonical="experience",
            category="experience",
            required=_required(sentence),
            source=sentence,
        ))

    low = text.lower()
    education_terms = [
        ("bachelor's degree", "bachelor"), ("bachelor degree", "bachelor"),
        ("bachelor", "bachelor"), ("computer science", "computer science"),
        ("statistics", "statistics"), ("mathematics", "mathematics"),
        ("economics", "economics"), ("information systems", "information systems"),
        ("information technology", "information technology"),
    ]
    if any(re.search(r"\b" + re.escape(term) + r"\b", low) for term, _ in education_terms):
        requirements.append(Requirement(
            name="Relevant bachelor's/quantitative education",
            canonical="education",
            category="education",
            required=True,
            source="Education requirement detected in job description.",
        ))

    return [r.to_dict() for r in requirements]
