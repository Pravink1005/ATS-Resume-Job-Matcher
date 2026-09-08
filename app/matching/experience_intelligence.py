from .experience_matcher import match_experience
class ExperienceIntelligence:
    def match(self,candidate,required,preferred=False): return match_experience(candidate,required,preferred)
