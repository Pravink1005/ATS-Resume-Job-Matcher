from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import ResumeRepository,JobRepository,MatchRepository,decode
from app.schemas.match_schema import MatchRequest
from app.services.matching_service import MatchingService
router=APIRouter(); service=MatchingService()
def build(x,job_title,requirement_analysis=None):
    arr=['matched_skills','missing_skills','exact_skill_matches','alias_skill_matches','partial_skill_matches','related_skill_matches','matched_competencies','missing_competencies','matched_keywords','missing_keywords','explanations']
    return {'match_id':x.id,'resume_id':x.resume_id,'job_id':x.job_id,'job_title':job_title,'overall_score':x.overall_score,'recommendation':x.recommendation,'component_scores':{'skills':x.skills_score,'experience':x.experience_score,'education':x.education_score,'competencies':x.competency_score,'keywords':x.keyword_score,'tfidf':x.tfidf_score},'weighted_scores':{},**{a:decode(getattr(x,a)) for a in arr},'experience_status':x.experience_status,'candidate_experience':x.candidate_experience,'required_experience':x.required_experience,'experience_gap':x.experience_gap,'education_status':x.education_status,'tfidf_similarity':x.tfidf_similarity,'requirement_analysis':requirement_analysis or []}
@router.post('/match')
def create_match(req:MatchRequest,db:Session=Depends(get_db)):
    r=ResumeRepository.get_by_id(db,req.resume_id); j=JobRepository.get_by_id(db,req.job_id)
    if not r or not j: raise HTTPException(status_code=404,detail='Resume or job not found')
    result=service.match(r.resume_text,j.job_description); payload={'resume_id':r.id,'job_id':j.id,'overall_score':result['overall_score'],'recommendation':result['recommendation'],'skills_score':result['component_scores']['skills'],'experience_score':result['component_scores']['experience'],'education_score':result['component_scores']['education'],'competency_score':result['component_scores']['competencies'],'keyword_score':result['component_scores']['keywords'],'tfidf_score':result['component_scores']['tfidf'],'candidate_experience':result['candidate_experience'],'required_experience':result['required_experience'],'experience_gap':result['experience_gap'],'experience_status':result['experience_status'],'education_status':result['education_status'],'tfidf_similarity':result['tfidf_similarity'],**{k:result[k] for k in ['matched_skills','missing_skills','exact_skill_matches','alias_skill_matches','partial_skill_matches','related_skill_matches','matched_competencies','missing_competencies','matched_keywords','missing_keywords','explanations']}}
    x=MatchRepository.create(db,payload); return build(x,j.job_title,result['requirement_analysis'])|{'weighted_scores':result['weighted_scores']}
@router.get('/match/{match_id}')
def get_match(match_id:int,db:Session=Depends(get_db)):
    x=MatchRepository.get_by_id(db,match_id)
    if not x: raise HTTPException(status_code=404,detail='Match not found')
    j=JobRepository.get_by_id(db,x.job_id)
    requirement_analysis = []
    if j:
        r = ResumeRepository.get_by_id(db, x.resume_id)
        if r:
            requirement_analysis = service.match(r.resume_text, j.job_description).get('requirement_analysis', [])
    return build(x,j.job_title if j else 'Unknown', requirement_analysis)
