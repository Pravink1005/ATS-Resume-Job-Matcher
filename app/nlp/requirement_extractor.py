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
    ("oci", "oci"), ("oracle cloud", "oci"), ("oke", "oke"),
    ("docker", "docker"), ("kubernetes", "kubernetes"), ("k8s", "kubernetes"),
    ("containers", "containers"), ("containerization", "containers"),
    ("jenkins", "jenkins"), ("git", "git"), ("github", "github"), ("gitlab", "gitlab"),
    ("terraform", "terraform"), ("ansible", "ansible"), ("ci/cd", "ci/cd"),
    ("linux", "linux"), ("sre", "sre"), ("devops", "devops"),
    # Observability & Telemetry
    ("prometheus", "prometheus"), ("grafana", "grafana"),
    ("opentelemetry", "opentelemetry"), ("open telemetry", "opentelemetry"), ("otel", "opentelemetry"),
    ("datadog", "datadog"), ("splunk", "splunk"),
    # Enterprise Security & Identity
    ("microsoft purview", "microsoft purview"), ("purview", "microsoft purview"),
    ("zscaler", "zscaler"), ("iam", "iam"),
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


PREFERRED_HEADERS = [
    r"preferred\s+(?:qualifications?|skills?|experience|requirements?)",
    r"nice\s+to\s+have",
    r"bonus\s+(?:points?|qualifications?)",
    r"desired\s+(?:qualifications?|skills?|experience)",
    r"what\s+would\s+make\s+you\s+stand\s+out",
    r"good\s+to\s+have",
]

REQUIRED_HEADERS = [
    r"required\s+(?:qualifications?|skills?|experience|requirements?)",
    r"minimum\s+(?:qualifications?|requirements?)",
    r"basic\s+(?:qualifications?|requirements?)",
    r"must\s+haves?",
    r"qualifications",
    r"requirements",
    r"what\s+you\s+need",
    r"what\s+you\s+bring",
    r"key\s+responsibilities",
    r"responsibilities",
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

    active_section_required = True
    scoped_sentences = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        low_line = line.lower()
        is_header = len(line.split()) <= 8 and (line.endswith(":") or not line.endswith("."))
        if is_header:
            if any(re.search(r"\b" + p + r"\b", low_line) for p in PREFERRED_HEADERS):
                active_section_required = False
                continue
            elif any(re.search(r"\b" + p + r"\b", low_line) for p in REQUIRED_HEADERS):
                active_section_required = True
                continue

        for s in re.split(r"(?<=[.!?])\s+", line):
            s_clean = s.strip()
            if s_clean:
                req_flag = active_section_required and _required(s_clean)
                scoped_sentences.append((s_clean, req_flag))

    if not scoped_sentences:
        scoped_sentences = [(s, _required(s)) for s in _sentences(text)]

    sentences = [s for s, _ in scoped_sentences]

    for sentence, required in scoped_sentences:
        low = sentence.lower()
        # Identify skills present in this sentence
        sentence_skills = []
        sentence_canons = set()
        suppressed = set()
        if re.search(r"\badvanced\s+sql\b", low):
            suppressed.add("sql")
        if re.search(r"\badvanced\s+excel\b", low):
            suppressed.add("excel")

        for display, canonical in SKILL_PATTERNS:
            if canonical in suppressed or canonical in seen or canonical in sentence_canons:
                continue
            if display in ("r programming", "r language"):
                m = bool(re.search(r"\br\s+(?:programming|language|studio)\b", low))
            elif display in ("go", "go programming", "go language"):
                m = bool(re.search(r"\bgo\s+(?:programming|language|developer|engineer)\b|\bgolang\b|(?:^|[,/|•\n:])\s*go\s*(?:[,/|•\n]|$)", low))
            else:
                m = bool(re.search(r"(?<!\w)" + re.escape(display) + r"(?!\w)", low))
            if m:
                sentence_skills.append((display, canonical))
                sentence_canons.add(canonical)

        # Build fine-grained alternative groups for skills explicitly in an "or" clause
        skill_alt_map = {}
        if re.search(r"\bor\b", low) and len(sentence_skills) >= 2:
            # 1. Parenthetical or clauses, e.g. "(OCI, AWS, or Azure)"
            for p in re.findall(r"\(([^)]*\bor\b[^)]*)\)", low):
                p_grp = "alt_" + hashlib.sha1(p.encode("utf-8")).hexdigest()[:8]
                for disp, canon in sentence_skills:
                    if re.search(r"(?<!\w)" + re.escape(disp) + r"(?!\w)", p):
                        skill_alt_map[canon] = p_grp

            # 2. Comma/space separated series ending in "or", e.g. "Python, Go, Java, or a comparable language"
            for o in re.findall(r"(?:[a-z0-9+#.]+(?:,\s*|\s+)){1,5}or\s+[a-z0-9+#.]+", low):
                matching = [canon for disp, canon in sentence_skills if re.search(r"(?<!\w)" + re.escape(disp) + r"(?!\w)", o)]
                if len(matching) >= 2:
                    o_grp = "alt_" + hashlib.sha1(o.encode("utf-8")).hexdigest()[:8]
                    for canon in matching:
                        skill_alt_map[canon] = o_grp

        for display, canonical in sentence_skills:
            req = Requirement(
                name=display,
                canonical=canonical,
                category="technical_skill",
                required=required,
                proficiency=_proficiency(sentence, display),
                alternative_group=skill_alt_map.get(canonical),
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
    exp = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:hands[- ]on\s+|professional\s+)?(?:data|analytics|bi|relevant|work)?\s*experience", text, re.I)
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
