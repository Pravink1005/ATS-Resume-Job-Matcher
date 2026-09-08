from .keyword_matcher import match_keywords
class KeywordIntelligence:
    def match(self,required,candidate): return match_keywords(required,candidate)
