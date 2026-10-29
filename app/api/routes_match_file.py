from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import ResumeRepository, JobRepository, MatchRepository
from app.services.resume_service import ResumeService
from app.services.matching_service import MatchingService
from .routes_match import build

router = APIRouter()
rs = ResumeService()
ms = MatchingService()

@router.post('/match/file')
async def match_file(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = await resume_file.read()
        text = rs.extract_text_from_file(data, resume_file.filename or '')
        jdata = ms.extract_job_data(job_description)
        r = ResumeRepository.create(db, resume_file.filename or 'resume', text)
        j = JobRepository.create(db, jdata['job_title'], job_description)
        result = ms.match(text, job_description)
        payload = {
            'resume_id': r.id,
            'job_id': j.id,
            'overall_score': result['overall_score'],
            'recommendation': result['recommendation'],
            'skills_score': result['component_scores']['skills'],
            'experience_score': result['component_scores']['experience'],
            'education_score': result['component_scores']['education'],
            'competency_score': result['component_scores']['competencies'],
            'keyword_score': result['component_scores']['keywords'],
            'tfidf_score': result['component_scores']['tfidf'],
            'candidate_experience': result['candidate_experience'],
            'required_experience': result['required_experience'],
            'experience_gap': result['experience_gap'],
            'experience_status': result['experience_status'],
            'education_status': result['education_status'],
            'tfidf_similarity': result['tfidf_similarity'],
            'requirement_analysis': result.get('requirement_analysis', []),
            'context_match': result.get('context_match', {}),
            'weighted_scores': result.get('weighted_scores', {}),
            **{k: result[k] for k in [
                'matched_skills', 'missing_skills', 'exact_skill_matches', 'alias_skill_matches',
                'partial_skill_matches', 'related_skill_matches', 'matched_competencies',
                'missing_competencies', 'matched_keywords', 'missing_keywords', 'explanations'
            ]}
        }
        x = MatchRepository.create(db, payload)
        return build(
            x,
            j.job_title,
            result['requirement_analysis'],
            result.get('context_match'),
            result.get('weighted_scores'),
            result.get('resume_health'),
            result.get('tailoring_suggestions')
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
