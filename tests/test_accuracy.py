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
    # Breakdown education score should not be 0.0; should receive full points
    assert res['weighted_scores']['education'] == 10.0
    assert res['overall_score'] >= 75.0
    assert res['recommendation'] in ('Good Match', 'Excellent Match')
