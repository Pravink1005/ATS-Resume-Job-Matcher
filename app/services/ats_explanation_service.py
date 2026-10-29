class ATSExplanationService:
    def explain(self, r):
        out = []
        if r.get('is_gated') and r.get('gate_reasons'):
            for reason in r['gate_reasons']:
                out.append(f"Production Safety Gate Enforced: {reason}")

        out.extend([
            'Overall ATS score is calculated from explicit requirement evidence; text similarity is only a weak supporting signal.',
            'Related technologies are not treated as equivalent skills (for example, SQL does not prove CTEs/complex joins, and Power BI does not prove Tableau/Looker).',
        ])
        if r.get('missing_skills'):
            out.append('Skills not explicitly demonstrated: ' + ', '.join(r['missing_skills']) + '.')
        if r.get('related_skill_matches'):
            out.append('Supporting relationships are informational only and do not increase the direct skill score: ' + ', '.join(r['related_skill_matches']) + '.')
        if r.get('experience_gap', 0) > 0:
            label = 'preferred' if r.get('preferred_experience') else 'stated requirement'
            out.append(f"Experience gap: {r['experience_gap']:g} year(s) compared with the {label}.")
        if r.get('education_status', '').startswith('Meets'):
            out.append('Education appears aligned with the stated requirement.')
        if r.get('matched_skills'):
            out.append('Direct skill evidence found for: ' + ', '.join(r['matched_skills']) + '.')
        if r.get('tfidf_similarity', 0) < .35:
            out.append('Resume wording has limited text similarity to the job description; this does not prove a missing skill.')
        return out
