class ScoringEngine:
    WEIGHTS={'skills':.35,'experience':.20,'education':.10,'competencies':.15,'keywords':.10,'tfidf':.10}
    def calculate(self,scores):
        weighted={k:round(float(scores.get(k,0))*w,2) for k,w in self.WEIGHTS.items()}
        total=round(sum(weighted.values()),2)
        if total>=85: rec='Excellent Match'
        elif total>=70: rec='Good Match'
        elif total>=55: rec='Moderate Match'
        else: rec='Low Match'
        return total,rec,weighted
