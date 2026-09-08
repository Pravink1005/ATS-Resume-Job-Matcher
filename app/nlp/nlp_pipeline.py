from .skill_extractor import extract_skills
from .experience_extractor import extract_experience
from .education_extractor import extract_education
from .competency_extractor import extract_competencies
from .keyword_extractor import extract_keywords
class NLPPipeline:
    def analyze(self,text):
        return {'skills':extract_skills(text),'experience':extract_experience(text),'education':extract_education(text),'competencies':extract_competencies(text),'keywords':extract_keywords(text)}
