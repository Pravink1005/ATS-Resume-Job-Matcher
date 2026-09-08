from .education_matcher import match_education
class EducationIntelligence:
    def match(self,resume,job): return match_education(resume,job)
