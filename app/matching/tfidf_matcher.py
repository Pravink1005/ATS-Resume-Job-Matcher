from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class TFIDFMatcher:
    def similarity(self,a,b):
        if not a.strip() or not b.strip(): return 0.0
        try:return float(cosine_similarity(TfidfVectorizer(ngram_range=(1,2),stop_words='english').fit_transform([a,b]))[0,1])
        except ValueError:return 0.0
