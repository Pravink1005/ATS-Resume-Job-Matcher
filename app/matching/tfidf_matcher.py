from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFMatcher:
    def similarity(self, a: str, b: str) -> float:
        if not isinstance(a, str) or not isinstance(b, str) or not a.strip() or not b.strip():
            return 0.0
        try:
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            matrix = vec.fit_transform([a, b])
            return float(cosine_similarity(matrix)[0, 1])
        except ValueError:
            return 0.0

    @staticmethod
    def calibrate_raw(raw: float) -> float:
        """Maps typical resume-JD overlap (0.05 to 0.40) to standard 20% - 100% curve."""
        if raw <= 0.0:
            return 0.0
        if raw <= 0.05:
            calibrated = raw * 400
        else:
            calibrated = 20.0 + (raw - 0.05) * (80.0 / 0.35)
        return round(max(0.0, min(100.0, calibrated)), 2)

    def calibrated_score(self, a: str, b: str) -> tuple[float, float]:
        """Returns (raw_similarity, calibrated_0_to_100)."""
        raw = self.similarity(a, b)
        return round(raw, 4), self.calibrate_raw(raw)


TfidfMatcher = TFIDFMatcher

