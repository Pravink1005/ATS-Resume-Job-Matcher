class ScoringEngine:
    WEIGHTS={'skills':.35,'experience':.20,'education':.10,'competencies':.15,'keywords':.10,'tfidf':.10}

    ATS_WEIGHTS = {
        'technical_skill': .35,
        'experience': .20,
        'education': .10,
        'competency': .10,
        'responsibility': .10,
        'title': .05,
        'context': .05,
        'tfidf': .05,
    }

    def calculate(self,scores):
        weighted={k:round(float(scores.get(k,0))*w,2) for k,w in self.WEIGHTS.items()}
        total=min(100.0, round(sum(weighted.values()),2))
        if total>=85: rec='Excellent Match'
        elif total>=70: rec='Good Match'
        elif total>=55: rec='Moderate Match'
        else: rec='Low Match'
        return total,rec,weighted

    def calculate_ats(self, requirements, experience_score=0, education_score=100,
                      tfidf_similarity=0, title_score=100, context_score=100, skills_score=None):
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

        raw_scores = {}
        for category in self.ATS_WEIGHTS:
            if category == 'experience':
                raw_scores[category] = float(experience_score)
            elif category == 'education':
                values = category_scores['education']
                raw_scores[category] = sum(values) / len(values) if values else float(education_score)
            elif category == 'title':
                raw_scores[category] = float(title_score)
            elif category == 'context':
                raw_scores[category] = float(context_score)
            elif category == 'tfidf':
                raw_scores[category] = float(tfidf_similarity)
            elif category == 'technical_skill':
                values = category_scores['technical_skill']
                if values:
                    req_avg = sum(values) / len(values)
                    if skills_score is not None:
                        raw_scores[category] = round((req_avg + float(skills_score)) / 2.0, 2)
                    else:
                        raw_scores[category] = req_avg
                elif skills_score is not None:
                    raw_scores[category] = float(skills_score)
                else:
                    raw_scores[category] = None
            elif category in ('competency', 'responsibility'):
                values = category_scores[category]
                if values:
                    raw_scores[category] = sum(values) / len(values)
                else:
                    # Job description did not state requirements for this category:
                    # mark inactive so candidate is not unfairly penalized 10-20%
                    raw_scores[category] = None
            else:
                values = category_scores[category]
                raw_scores[category] = sum(values) / len(values) if values else 0.0

        active_categories = {k: v for k, v in raw_scores.items() if v is not None}
        total_active_weight = sum(self.ATS_WEIGHTS[cat] for cat in active_categories) or 1.0

        breakdown = {}
        for category in self.ATS_WEIGHTS:
            if category in active_categories:
                normalized_weight = self.ATS_WEIGHTS[category] / total_active_weight
                category_score = max(0.0, min(100.0, active_categories[category]))
                breakdown[category] = round(category_score * normalized_weight, 2)
            else:
                breakdown[category] = 0.0

        total = min(100.0, round(sum(breakdown.values()), 2))

        # Incomplete / Low-Detail Job Description Guard:
        # If the job description specified NO technical skills at all, an ATS cannot reliably verify fit.
        # Gate score at Moderate Match (<= 55%) to prevent false 90%+ scores on 1-line teasers.
        if raw_scores.get('technical_skill') is None:
            total = min(total, 55.0)

        # Core Technical Qualification Gate:
        # If candidate misses more than half of the required technical skills (< 50%),
        # overall ATS score must be gated at Moderate Match (< 60%) to prevent false positives.
        req_tech_avg = raw_scores.get('technical_skill') or 0.0
        if req_tech_avg < 50.0 or (skills_score is not None and float(skills_score) < 50.0 and req_tech_avg < 60.0):
            total = min(total, 58.0)

        if total >= 85:
            recommendation = 'Excellent Match'
        elif total >= 70:
            recommendation = 'Good Match'
        elif total >= 55:
            recommendation = 'Moderate Match'
        else:
            recommendation = 'Low Match'
        return total, recommendation, breakdown
