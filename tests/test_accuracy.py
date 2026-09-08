from app.nlp.experience_extractor import extract_experience
from app.nlp.skill_extractor import extract_skills
from app.nlp.keyword_extractor import extract_keywords
from app.matching.skill_matcher import SkillMatcher


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
