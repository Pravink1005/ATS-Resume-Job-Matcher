"""Evidence-based requirement matching for ATS scoring.

Important rule: semantic similarity is never treated as proof of a skill.
A requirement is matched only when the resume contains the same skill/phrase,
a true alias, or a conservative evidence phrase for a responsibility.
"""
import re
from app.matching.skill_normalizer import ALIASES, normalize_skill

# Conservative evidence phrases for requirements that are responsibilities/concepts.
# The phrase must actually occur in the resume; we never infer it from another tool.
EVIDENCE_PATTERNS = {
    "data extraction": [
        r"\bdata extraction\b", r"\bextract(?:ed|ing)?\s+(?:data|records|information)\b",
        r"\bcollect(?:ed|ing)?\s+(?:data|records|information)\b",
    ],
    "data cleaning": [
        r"\bdata cleaning\b", r"\bclean(?:ed|ing)?\s+(?:data|datasets?|records)\b",
        r"\bdata cleansing\b", r"\bpreprocess(?:ed|ing)?\b",
    ],
    "reporting": [
        r"\breporting\b", r"\breport generation\b", r"\bgenerat(?:ed|ing)\s+(?:reports?|report)\b",
        r"\bautomated reports?\b",
    ],
    "dashboard": [r"\bdashboards?\b"],
    "dashboard design": [r"\bdashboard design\b", r"\bdesigned?\s+(?:a|the|an)?\s*dashboards?\b"],
    "trend analysis": [r"\btrend analysis\b", r"\banaly[sz](?:ed|ing)?\s+(?:trends?|trend)\b"],
    "eda": [r"\bexploratory data analysis\b", r"\b\beda\b"],
    "kpi": [r"\bkpis?\b", r"\bkey performance indicators?\b"],
    "data governance": [r"\bdata governance\b"],
    "actionable insights": [r"\bactionable insights?\b"],
    "business insights": [r"\bbusiness insights?\b"],
    "cross-functional": [r"\bcross[- ]functional\b"],
    "stakeholder management": [r"\bstakeholder management\b", r"\bmanaged?\s+stakeholders?\b"],
    "communication": [r"\bcommunication skills?\b", r"\bcommunicat(?:ed|ing)\b"],
    "code review": [r"\bcode\s+reviews?\b", r"\breview(?:ed|ing)?\s+code\b"],
    "system design": [r"\bsystem\s+design\b", r"\barchitect(?:ed|ing)?\b"],
    "agile": [r"\bagile\b", r"\bscrum\b"],
    "scrum": [r"\bscrum\b", r"\bagile\b"],
    "data pipeline": [r"\bdata\s+pipelines?\b", r"\bpipelines?\b"],
    "data modeling": [r"\bdata\s+model(?:ing|ling)?\b"],
    "problem solving": [r"\bproblem[- ]solving\b", r"\bsolve\s+complex\s+problems\b"],
    "collaboration": [r"\bcollaborat(?:ed|ing|ion)\b", r"\bteam\s+player\b"],
    "leadership": [r"\bleadership\b", r"\bled\s+(?:a|the)?\s*team\b", r"\bmentoring\b", r"\bmentored\b"],
    # Cloud, DevOps, Observability & Security Evidence
    "prometheus": [r"\bprometheus\b"],
    "grafana": [r"\bgrafana\b"],
    "opentelemetry": [r"\bopentelemetry\b", r"\botel\b", r"\bopen\s+telemetry\b", r"\bdistributed\s+tracing\b"],
    "zscaler": [r"\bzscaler\b", r"\bzia\b", r"\bzpa\b"],
    "microsoft purview": [r"\bpurview\b", r"\bmicrosoft\s+purview\b"],
    "oci": [r"\boci\b", r"\boracle\s+cloud\b"],
    "iam": [r"\biam\b", r"\bidentity\s+(?:and|&)\s+access\b"],
    "sre": [r"\bsre\b", r"\bsite\s+reliability\b"],
    "devops": [r"\bdevops\b"],
    "containers": [r"\bcontainers?\b", r"\bdocker\b", r"\bcontaineriz(?:ed|ation)\b"],
}


def _snippet(text: str, start: int, end: int, window: int = 100) -> str:
    left = max(0, start - window)
    right = min(len(text), end + window)
    return " ".join(text[left:right].split())


def _find_pattern(text: str, patterns):
    low = text.lower()
    for pattern in patterns:
        m = re.search(pattern, low, re.I)
        if m:
            return m, _snippet(text, m.start(), m.end())
    return None, ""


def _explicit_skill(text: str, canonical: str):
    low = text.lower()
    # High-risk phrases must be explicit. SQL alone does not prove advanced SQL,
    # CTEs, complex joins, or query optimization.
    strict = {
        "r": [r"\br\s+(?:programming|language|studio)\b", r"\busing\s+r\b", r"\bprogramming\s+in\s+r\b"],
        "cte": [r"\bctes?\b", r"\bcommon table expressions?\b"],
        "advanced sql": [r"\badvanced\s+sql\b"],
        "complex joins": [r"\bcomplex\s+joins?\b"],
        "query optimization": [r"\bquery\s+optimization\b", r"\bquery\s+optimisation\b"],
        "advanced excel": [r"\badvanced\s+(?:microsoft\s+)?excel\b"],
        "power bi": [r"\bpower\s*bi\b", r"\bmicrosoft\s+power\s*bi\b"],
        "data visualization": [r"\bdata\s+visuali[sz]ation\b"],
        "tableau": [r"\btableau\b"],
        "looker": [r"\blooker\b"],
        "excel": [r"\bexcel\b", r"\bmicrosoft\s+excel\b"],
        "sql": [r"\bsql\b", r"\bstructured query language\b"],
        "python": [r"\bpython\b"],
        "pandas": [r"\bpandas\b"],
        "numpy": [r"\bnumpy\b"],
        "mysql": [r"\bmysql\b"],
        "postgresql": [r"\bpostgresql\b", r"\bpostgres\b"],
        "go": [r"\bgo\s+(?:programming|language)\b", r"\bprogramming\s+in\s+go\b", r"\bgolang\b"],
        "react": [r"\breact(?:\.js|js)?\b"],
        "next.js": [r"\bnext(?:\.js|js)?\b"],
        "node.js": [r"\bnode(?:\.js|js)?\b"],
        "vue": [r"\bvue(?:\.js|js)?\b"],
        "angular": [r"\bangular(?:\.js|js)?\b"],
        "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "fastapi": [r"\bfastapi\b", r"\bfast\s+api\b"],
        "spring boot": [r"\bspring\s*boot\b"],
        "ci/cd": [r"\bci\s*/\s*cd\b", r"\bci-cd\b", r"\bcicd\b"],
    }
    patterns = strict.get(canonical, [r"(?<!\w)" + re.escape(canonical) + r"(?!\w)"])
    return _find_pattern(text, patterns)


class EvidenceMatcher:
    # Confidence values are deliberately conservative. They are not a hidden
    # score boost; the evidence text is returned with every matched requirement.
    CONFIDENCE = {
        "exact": 1.00,
        "alias": 1.00,
        "strong_evidence": 0.85,
        "missing": 0.00,
    }

    def _alias_match(self, resume_text: str, canonical: str):
        low = resume_text.lower()
        for alias, target in ALIASES.items():
            if target != canonical:
                continue
            m = re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", low)
            if m:
                return _snippet(resume_text, m.start(), m.end())
        return ""

    def match_requirements(self, requirements, resume_text, resume_skills=None):
        resume_skills = {normalize_skill(x) for x in (resume_skills or [])}
        results = []

        for req in requirements:
            # Experience and education are not text skills. They are evaluated by
            # dedicated numeric/education matchers in MatchingService.
            if req.get("category") in {"experience", "education"}:
                results.append({
                    **req, "status": "pending", "match_type": "not_text_matched",
                    "score": 0.0, "confidence": 0.0,
                    "evidence": "Evaluated by the dedicated experience/education matcher.",
                    "evidence_source": "dedicated_matcher",
                })
                continue

            canonical = normalize_skill(req["canonical"])

            # 1) Exact explicit evidence.
            m, snippet = _explicit_skill(resume_text, canonical)
            if m:
                results.append({
                    **req, "status": "matched", "match_type": "exact",
                    "score": 100.0, "confidence": self.CONFIDENCE["exact"],
                    "evidence": snippet, "evidence_source": "resume_text",
                })
                continue

            # 2) True alias only (never a related technology).
            alias_snippet = self._alias_match(resume_text, canonical)
            if alias_snippet:
                results.append({
                    **req, "status": "matched", "match_type": "alias",
                    "score": 100.0, "confidence": self.CONFIDENCE["alias"],
                    "evidence": alias_snippet, "evidence_source": "resume_text_alias",
                })
                continue

            # 3) Skill extractor evidence. This is still explicit evidence because
            # the extractor only returns skills found in the resume text.
            if canonical in resume_skills:
                results.append({
                    **req, "status": "matched", "match_type": "exact",
                    "score": 100.0, "confidence": self.CONFIDENCE["exact"],
                    "evidence": f"Explicit skill detected: {canonical}.",
                    "evidence_source": "resume_skill_extractor",
                })
                continue

            # 4) Conservative responsibility evidence.
            patterns = EVIDENCE_PATTERNS.get(canonical, [])
            if patterns:
                m, snippet = _find_pattern(resume_text, patterns)
                if m:
                    results.append({
                        **req, "status": "matched", "match_type": "strong_evidence",
                        "score": 85.0, "confidence": self.CONFIDENCE["strong_evidence"],
                        "evidence": snippet, "evidence_source": "resume_context",
                    })
                    continue

            results.append({
                **req, "status": "missing", "match_type": "missing",
                "score": 0.0, "confidence": self.CONFIDENCE["missing"],
                "evidence": "No explicit supporting evidence found in resume.",
                "evidence_source": "none",
            })

        return results
