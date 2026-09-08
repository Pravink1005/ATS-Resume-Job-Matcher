class HybridMatcher:
    def combine(self,skill_score,tfidf_score): return round(.75*skill_score+.25*tfidf_score,2)
