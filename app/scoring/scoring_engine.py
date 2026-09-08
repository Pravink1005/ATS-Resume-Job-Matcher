class ScoringEngine:
    WEIGHTS={'skills':.35,'experience':.20,'education':.10,'competencies':.15,'keywords':.10,'tfidf':.10}

    ATS_WEIGHTS = {
        'technical_skill': .35,
        'experience': .20,
        'education': .10,
        'competency': .10,
        'responsibility': .15,
        'tfidf': .10,
    }

    def calculate(self,scores):
        weighted={k:round(float(scores.get(k,0))*w,2) for k,w in self.WEIGHTS.items()}
        total=round(sum(weighted.values()),2)
        if total>=85: rec='Excellent Match'
        elif total>=70: rec='Good Match'
        elif total>=55: rec='Moderate Match'
        else: rec='Low Match'
        return total,rec,weighted

    def calculate_ats(self, requirements, experience_score=0, tfidf_similarity=0):
        """Calculate the explainable score from structured requirement evidence."""
        category_scores = {category: [] for category in self.ATS_WEIGHTS if category != 'tfidf'}
        alternative_groups = {}

        for requirement in requirements or []:
            category = requirement.get('category')
            if category not in category_scores:
                continue

            score = max(0.0, min(100.0, float(requirement.get('score', 0))))
            group = requirement.get('alternative_group')
            if group:
                alternative_groups.setdefault((category, group), []).append(score)
            else:
                category_scores[category].append(score)

        # An alternative group is one requirement slot; taking the best evidence
        # prevents an "A or B" requirement from being counted twice.
        for (category, _), scores in alternative_groups.items():
            category_scores[category].append(max(scores))

        breakdown = {}
        for category, weight in self.ATS_WEIGHTS.items():
            if category == 'experience':
                score = float(experience_score)
            elif category == 'tfidf':
                score = float(tfidf_similarity) * 100
            else:
                values = category_scores[category]
                score = sum(values) / len(values) if values else 0.0
            score = max(0.0, min(100.0, score))
            breakdown[category] = round(score * weight, 2)

        total = round(sum(breakdown.values()), 2)
        if total >= 85:
            recommendation = 'Excellent Match'
        elif total >= 70:
            recommendation = 'Good Match'
        elif total >= 55:
            recommendation = 'Moderate Match'
        else:
            recommendation = 'Low Match'
        return total, recommendation, breakdown
