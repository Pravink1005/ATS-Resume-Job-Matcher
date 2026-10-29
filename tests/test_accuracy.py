from app.nlp.experience_extractor import extract_experience
from app.nlp.skill_extractor import extract_skills
from app.nlp.keyword_extractor import extract_keywords
from app.nlp.competency_extractor import extract_competencies
from app.matching.skill_matcher import SkillMatcher
from app.matching.context_matcher import match_context
from app.scoring.scoring_engine import ScoringEngine
from app.services.matching_service import MatchingService


def test_experience_date_range_present():
    text = "Professional Experience\nJunior Process Associate\nJul 2025 - Present\n\nEducation\nB.Sc IT"
    assert extract_experience(text) > 0


def test_numeric_date_ranges_and_hands_on_experience():
    text = """
    PRAVIN KUMAR A
    PROFESSIONAL SUMMARY
    Data professional with 1+ year of hands-on experience building, monitoring, and optimizing ETL/ELT pipelines

    PROFESSIONAL EXPERIENCE
    Junior Process Associate | Aggregate Intelligence 07/2025 – 07/2026
    • Monitored and executed Python-based ETL jobs
    Data Analytics Intern | HCL Technologies 12/2024 – 02/2025
    • Contributed to an AI-powered Project Cost Estimation system

    EDUCATION
    M.Sc. Data Science and Business Analysis 08/2023 – 05/2025
    B.Sc. Information Technology 08/2020 – 05/2023
    """
    exp = extract_experience(text)
    # 07/2025 - 07/2026 (13 mos) + 12/2024 - 02/2025 (3 mos) = 16 mos = 1.33 yrs -> formats as 1.3 yrs
    assert exp >= 1.3
    assert f"{exp:.1f}" == "1.3"


def test_r_is_not_false_positive():
    skills = extract_skills("Bachelor degree in Information Technology. Python, SQL, Excel, Power BI.")
    assert 'r' not in skills


def test_explicit_r_is_detected():
    skills = extract_skills("Skills: Python, SQL and R programming")
    assert 'r' in skills


def test_keyword_extractor_is_curated():
    kws = extract_keywords("Ability to build accurate dashboards across business teams using advanced SQL and Power BI.")
    assert 'advanced sql' in kws
    assert 'power bi' in kws
    assert 'ability' not in kws
    assert 'across' not in kws


def test_skill_match_does_not_match_single_letter_r():
    result = SkillMatcher().match(['r'], ['python', 'sql'])
    assert result['score'] == 0.0
    assert result['missing'] == ['r']


def test_title_and_seniority_match():
    result = match_context('Senior Data Analyst with Python experience', 'Senior Data Analyst', '')
    assert result['title_match_score'] == 100.0
    assert result['seniority_score'] == 100.0


def test_location_and_authorization_are_evidence_based():
    result = match_context(
        'Data Analyst based in Toronto. Authorized to work without sponsorship.',
        'Data Analyst',
        'Location: Toronto. Must be authorized to work without sponsorship.',
    )
    assert result['location_score'] == 100.0
    assert result['authorization_score'] == 100.0


def test_missing_context_evidence_is_uncertain_not_match():
    result = match_context('Data Analyst', 'Data Analyst', 'Location: Toronto')
    assert result['location_score'] == 50.0


def test_ats_weights_sum_to_one():
    total_weight = round(sum(ScoringEngine.ATS_WEIGHTS.values()), 4)
    assert total_weight == 1.0


def test_competency_boundary_safe():
    # 'miscommunication' or 'incompetence' should not trigger 'communication'
    res = extract_competencies('Handling miscommunication and organizational conflicts.')
    assert 'communication' not in res

    # True explicit competency is found
    res2 = extract_competencies('Excellent communication and leadership skills.')
    assert 'communication' in res2
    assert 'leadership' in res2


def test_education_not_penalized_when_not_in_job_description():
    svc = MatchingService()
    # Job description does not specify an education requirement
    job_desc = "Data Analyst\nRequired: Python, SQL\nExperience: 2 years"
    resume = "Data Analyst\nSkills: Python, SQL\nExperience: 3 years"
    res = svc.match(resume, job_desc)
    # Breakdown education score should receive its full dynamic weight (>= 10.0)
    assert res['weighted_scores']['education'] >= 10.0
    assert res['overall_score'] >= 75.0
    assert res['recommendation'] in ('Good Match', 'Excellent Match')


def test_dynamic_weight_rebalancing_high_match():
    svc = MatchingService()
    # Concise job description without competencies or responsibilities sections
    job_desc = """
    Job Title: Senior Python Developer
    Required: Python, Docker, PostgreSQL
    Experience: 5 years
    """
    resume = """
    Senior Python Developer
    Skills: Python, Docker, PostgreSQL
    Experience: 6 years
    """
    res = svc.match(resume, job_desc)
    # Candidate should not lose 20% due to unstated categories; score should be >= 90
    assert res['overall_score'] >= 90.0
    assert res['recommendation'] == 'Excellent Match'


def test_modern_frontend_role_matching():
    svc = MatchingService()
    job_desc = """
    Job Title: Senior Front-End Engineer
    Required: React, Next.js, TypeScript, Tailwind
    Experience: 4 years
    """
    resume = """
    Senior Front-End Engineer
    Skills: React.js, NextJS, TypeScript, Tailwind, Git
    Experience: 5 years
    """
    res = svc.match(resume, job_desc)
    assert res['overall_score'] >= 85.0
    assert res['recommendation'] == 'Excellent Match'
    matched_canons = [
        r['canonical'] for r in res['requirement_analysis']
        if r.get('status') == 'matched'
    ]
    assert 'react' in matched_canons
    assert 'next.js' in matched_canons
    assert 'typescript' in matched_canons


def test_backend_cloud_alias_matching():
    svc = MatchingService()
    job_desc = """
    Job Title: Backend Engineer
    Required: Go, Kubernetes, FastAPI, PostgreSQL
    Experience: 3 years
    """
    resume = """
    Backend Engineer
    Skills: Golang, K8s, Fast API, Postgres
    Experience: 4 years
    """
    res = svc.match(resume, job_desc)
    assert res['overall_score'] >= 85.0
    matched_canons = [
        r['canonical'] for r in res['requirement_analysis']
        if r.get('status') == 'matched'
    ]
    assert 'go' in matched_canons
    assert 'kubernetes' in matched_canons
    assert 'fastapi' in matched_canons
    assert 'postgresql' in matched_canons


def test_calibrated_tfidf_curve():
    from app.matching.tfidf_matcher import TfidfMatcher
    matcher = TfidfMatcher()
    # Zero raw similarity gives 0
    assert matcher.calibrate_raw(0.0) == 0.0
    # Realistic similarity of 0.20 maps to ~54+ on the grade curve
    score_20 = matcher.calibrate_raw(0.20)
    assert score_20 >= 50.0
    # Strong similarity of 0.35+ maps to >= 85
    score_35 = matcher.calibrate_raw(0.35)
    assert score_35 >= 85.0
    # Saturated similarity maps to 100
    assert matcher.calibrate_raw(0.50) == 100.0


def test_missing_core_skills_gated_to_moderate_match():
    svc = MatchingService()
    # Job requires heavy DevOps / SRE tools (Kubernetes, Linux, Terraform, Go, Java, Azure, AWS, Git, CI/CD)
    job_desc = """
    Job Title: Senior Platform Engineer
    Key Responsibilities: Build automated pipelines, monitor environments, resolve issues.
    Required Qualifications:
    Hands-on experience with Linux, Git, containers, Kubernetes, and at least one major cloud platform (OCI, AWS, or Azure).
    Experience developing infrastructure-as-code modules using Terraform.
    Proficiency in Python, Go, Java, or a comparable language.
    Experience building CI/CD pipelines.
    """
    # Candidate only has Python, Git, AWS, and CI/CD (missing Kubernetes, Linux, Terraform, Go, Java, Azure)
    resume = """
    Pravin Kumar
    Junior Data Professional
    Experience: 1.3 years
    Skills: Python, SQL, AWS, Git, CI/CD, Tableau
    Education: B.Sc. Information Technology
    """
    res = svc.match(resume, job_desc)
    # The candidate is missing > 50% of the core technical requirements
    # Overall score must be gated at Moderate Match (< 60%), never an inflated 'Excellent Match'
    assert res['overall_score'] <= 60.0
    assert res['recommendation'] in ('Moderate Match', 'Low Match')
    assert 'kubernetes' in res['missing_skills']
    assert 'linux' in res['missing_skills']
    assert 'terraform' in res['missing_skills']


