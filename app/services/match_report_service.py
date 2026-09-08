from app.database.repository import decode
class MatchReportService:
    def from_record(self,x):
        fields=['matched_skills','missing_skills','exact_skill_matches','alias_skill_matches','partial_skill_matches','related_skill_matches','matched_competencies','missing_competencies','matched_keywords','missing_keywords','explanations']
        d={f:decode(getattr(x,f)) for f in fields}; return d
