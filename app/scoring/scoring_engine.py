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
                      tfidf_similarity=0, title_score=100, context_score=100, skills_score=None,
                      candidate_experience=None, required_experience=None, return_gates=False):
        """Calculate the explainable score from structured requirement evidence with production safety gates."""
        category_scores = {category: [] for category in self.ATS_WEIGHTS if category != 'tfidf'}
        alternative_groups = {}

        mandatory_tech_scores = []
        preferred_tech_scores = []

        for requirement in requirements or []:
            category = requirement.get('category')
            if category not in category_scores:
                continue

            score = max(0.0, min(100.0, float(requirement.get('score', 0))))
            is_req = requirement.get('required', True)
            group = requirement.get('alternative_group')

            if group:
                alternative_groups.setdefault((category, group, is_req), []).append(score)
            else:
                if category == 'technical_skill':
                    if is_req:
                        mandatory_tech_scores.append(score)
                    else:
                        preferred_tech_scores.append(score)
                category_scores[category].append(score)

        # An alternative group is one requirement slot; taking the best evidence
        # prevents an "A or B" requirement from being counted twice.
        for (category, _, is_req), scores in alternative_groups.items():
            best = max(scores)
            if category == 'technical_skill':
                if is_req:
                    mandatory_tech_scores.append(best)
                else:
                    preferred_tech_scores.append(best)
            category_scores[category].append(best)

        raw_scores = {}
        mand_avg = None
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
                # Distinguish mandatory vs preferred technical skills
                if mandatory_tech_scores and preferred_tech_scores:
                    mand_avg = sum(mandatory_tech_scores) / len(mandatory_tech_scores)
                    pref_avg = sum(preferred_tech_scores) / len(preferred_tech_scores)
                    req_avg = round(0.85 * mand_avg + 0.15 * pref_avg, 2)
                elif mandatory_tech_scores:
                    mand_avg = sum(mandatory_tech_scores) / len(mandatory_tech_scores)
                    req_avg = mand_avg
                elif preferred_tech_scores:
                    pref_avg = sum(preferred_tech_scores) / len(preferred_tech_scores)
                    req_avg = pref_avg
                else:
                    req_avg = None

                if req_avg is not None:
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

        # ==============================================================================
        # PRODUCTION SAFETY & RECRUITER KNOCKOUT GATES
        # ==============================================================================
        applied_gates = []
        gate_reasons = []

        # 1. Seniority Knockout Gate:
        # If the job requires 5+ years (Senior, Lead, Staff, Principal) and candidate has < 40% tenure
        # or tenure deficit is > 3.5 years, candidate fails minimum seniority threshold.
        req_exp_val = float(required_experience or 0.0)
        cand_exp_val = float(candidate_experience or 0.0)
        if req_exp_val >= 5.0 and (cand_exp_val < (0.40 * req_exp_val) or (req_exp_val - cand_exp_val) > 3.5):
            gap = round(req_exp_val - cand_exp_val, 1)
            applied_gates.append('seniority_knockout')
            gate_reasons.append(
                f"Seniority Knockout: Role requires {req_exp_val:g} yrs (Senior/Staff level); "
                f"candidate has {cand_exp_val:g} yrs (tenure deficit of {gap:g} yrs)."
            )
            total = min(total, 45.0)
        elif req_exp_val >= 3.0 and (cand_exp_val < (0.30 * req_exp_val) or (req_exp_val - cand_exp_val) > 2.5):
            gap = round(req_exp_val - cand_exp_val, 1)
            applied_gates.append('seniority_knockout')
            gate_reasons.append(
                f"Seniority Knockout: Role requires {req_exp_val:g} yrs; "
                f"candidate has {cand_exp_val:g} yrs (tenure deficit of {gap:g} yrs)."
            )
            total = min(total, 48.0)

        # 2. Incomplete / Low-Detail Job Description Guard:
        # If the job description specified NO technical skills at all, an ATS cannot reliably verify fit.
        # Gate score at Moderate Match (<= 55%) to prevent false 90%+ scores on 1-line teasers.
        if raw_scores.get('technical_skill') is None:
            applied_gates.append('incomplete_jd_guard')
            gate_reasons.append("Incomplete Job Description: No verifiable technical skills detected in posting; score capped at 55%.")
            total = min(total, 55.0)

        # 3. Core Technical Qualification Gate:
        # If candidate misses more than half of the mandatory technical skills (< 50%),
        # overall ATS score must be gated at Moderate Match (< 60%) to prevent false positives.
        eval_tech = mand_avg if mand_avg is not None else (raw_scores.get('technical_skill') or 0.0)
        if eval_tech < 50.0 or (skills_score is not None and float(skills_score) < 50.0 and eval_tech < 60.0):
            applied_gates.append('technical_qualification_gate')
            gate_reasons.append(
                f"Core Technical Qualification Gate: Candidate matched only {eval_tech:.1f}% of core mandatory skills (required threshold: >=50%)."
            )
            total = min(total, 58.0)

        if total >= 85:
            recommendation = 'Excellent Match'
        elif total >= 70:
            recommendation = 'Good Match'
        elif total >= 55:
            recommendation = 'Moderate Match'
        else:
            recommendation = 'Low Match'

        if return_gates:
            return total, recommendation, breakdown, applied_gates, gate_reasons
        return total, recommendation, breakdown
