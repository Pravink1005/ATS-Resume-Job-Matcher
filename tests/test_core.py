import pytest
from app.utils.filename_utils import FilenameUtils
from app.utils.file_validator import FileValidator
from app.core.exceptions import InvalidResumeException
from app.matching.skill_normalizer import normalize_skill
from app.matching.skill_matcher import SkillMatcher
from app.services.matching_service import MatchingService

def test_filename():
    assert FilenameUtils.sanitize('../../my resume!.pdf') == 'my_resume_.pdf'

def test_empty_filename():
    assert FilenameUtils.sanitize('') == 'resume'

def test_invalid_filename_type():
    with pytest.raises(TypeError):
        FilenameUtils.sanitize(None)

def test_file_validator():
    assert FileValidator.validate('resume.pdf', b'%PDF-1.4 sample content') == '.pdf'
    assert FileValidator.validate('resume.docx', b'PK\x03\x04sample content') == '.docx'
    assert FileValidator.validate('resume.txt', b'Plain text resume') == '.txt'

def test_file_validator_invalid_magic():
    with pytest.raises(InvalidResumeException):
        FileValidator.validate('fake.pdf', b'NOT_A_PDF_HEADER')
    with pytest.raises(InvalidResumeException):
        FileValidator.validate('fake.docx', b'NOT_A_ZIP_HEADER')

def test_skill_alias():
    assert normalize_skill('PowerBI') == 'power bi'

def test_skill_match():
    r = SkillMatcher().match(['sql', 'power bi'], ['mysql', 'powerbi'])
    assert 'sql' in r['matched'] and 'power bi' in r['matched']

def test_matching_service():
    s = MatchingService()
    r = s.match(
        'Python SQL pandas Excel Power BI B.Sc Information Technology 1 year experience',
        'Data Analyst\nPython SQL Excel Power BI\n2 years experience\nBachelor degree in Information Technology'
    )
    assert 0 <= r['overall_score'] <= 100
    assert 'python' in r['matched_skills']

def test_empty_resume_data():
    assert MatchingService().extract_resume_data('') is None

def test_empty_job_data():
    assert MatchingService().extract_job_data('') is None
