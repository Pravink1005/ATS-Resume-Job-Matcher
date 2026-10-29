from .skill_normalizer import normalize_skill, normalize_skills

RELATED = {
    'sql': {'mysql','postgresql','database','complex joins','cte','query optimization'},
    'complex joins': {'sql'},
    'cte': {'sql'},
    'query optimization': {'sql'},
    'data cleaning': {'data validation','data quality','etl','preprocessing'},
    'data validation': {'data cleaning','data quality','etl'},
    'data extraction': {'etl','sql','database'},
    'data visualization': {'power bi','tableau','looker','streamlit','dashboard'},
    'dashboard': {'power bi','tableau','looker','streamlit','data visualization'},
    'reporting': {'power bi','tableau','looker','dashboard','data visualization'},
    'power bi': {'dashboard','data visualization','bi'},
    'tableau': {'dashboard','data visualization','bi'},
    'looker': {'dashboard','data visualization','bi'},
    'python': {'pandas','numpy'},
    'pandas': {'python'},
    'numpy': {'python'},
    'eda': {'exploratory data analysis','trend analysis','analysis'},
    'etl': {'data extraction','data cleaning','data processing'},
    # Cloud, DevOps & Observability
    'aws': {'cloud platform', 'azure', 'gcp', 'oci'},
    'azure': {'cloud platform', 'aws', 'gcp', 'oci'},
    'gcp': {'cloud platform', 'aws', 'azure', 'oci'},
    'oci': {'cloud platform', 'aws', 'azure', 'gcp'},
    'kubernetes': {'docker', 'containers', 'oke', 'eks', 'aks'},
    'docker': {'kubernetes', 'containers'},
    'containers': {'docker', 'kubernetes'},
    'terraform': {'ansible', 'iac'},
    'prometheus': {'grafana', 'opentelemetry'},
    'grafana': {'prometheus', 'opentelemetry'},
    'opentelemetry': {'prometheus', 'grafana'},
    # Enterprise Security
    'microsoft purview': {'zscaler', 'iam'},
    'zscaler': {'microsoft purview', 'iam'},
    'iam': {'microsoft purview', 'zscaler'},
}


class SkillMatcher:
    def match(self, required, candidate):
        req = normalize_skills(required)
        cand = set(normalize_skills(candidate))
        exact, alias, partial, related, missing = [], [], [], [], []

        for r in req:
            if r in cand:
                exact.append(r)
                continue
            canonical = normalize_skill(r)
            if canonical in cand:
                alias.append(r)
                continue
            if len(r) > 2 and any(len(c) > 2 and (r in c or c in r) for c in cand):
                partial.append(r)
                continue
            if any(x in cand for x in RELATED.get(r, set())):
                related.append(r)
                continue
            missing.append(r)

        # Only exact/alias/partial matches affect the skill score.
        score = (
            (len(exact) + .95 * len(alias) + .65 * len(partial)) / len(req) * 100
            if req else 100.0
        )
        return {
            'score': round(score, 2),
            'matched': sorted(exact + alias + partial),
            'missing': sorted(missing + related),
            'exact': sorted(exact),
            'alias': sorted(alias),
            'partial': sorted(partial),
            'related': sorted(related),
        }
