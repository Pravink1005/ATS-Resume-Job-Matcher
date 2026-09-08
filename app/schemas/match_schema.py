from pydantic import BaseModel,Field
from typing import Any
class MatchRequest(BaseModel): resume_id:int; job_id:int
class MatchResponse(BaseModel):
    match_id:int; resume_id:int; job_id:int; job_title:str; overall_score:float; recommendation:str
    component_scores:dict[str,float]; weighted_scores:dict[str,float]
    matched_skills:list[str]; missing_skills:list[str]; exact_skill_matches:list[str]; alias_skill_matches:list[str]; partial_skill_matches:list[str]; related_skill_matches:list[str]
    matched_competencies:list[str]; missing_competencies:list[str]; matched_keywords:list[str]; missing_keywords:list[str]
    experience_status:str; candidate_experience:float; required_experience:float; experience_gap:float; education_status:str; tfidf_similarity:float; explanations:list[str]
    requirement_analysis:list[dict[str, Any]] = Field(default_factory=list)
