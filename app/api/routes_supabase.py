from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from app.services.supabase_service import SupabaseJobService
from app.services.resume_service import ResumeService
from app.services.job_recommender_service import JobRecommenderService

router = APIRouter(prefix='/supabase', tags=['Supabase Jobs'])
supabase_service = SupabaseJobService()
recommender_service = JobRecommenderService()
resume_service = ResumeService()


@router.get('/status')
def get_status():
    return supabase_service.get_status()


@router.get('/keywords')
def get_keywords():
    return {'keywords': supabase_service.get_distinct_keywords()}


@router.get('/jobs')
def search_jobs(
    query: str = Query('', description='Search by job title, company, or skills'),
    keyword: str = Query('', description='Filter by search keyword / role category'),
    time_frame: str = Query('all', description='Filter by time posted (24h, 3d, 7d, 30d, all)'),
    limit: int = Query(40, ge=1, le=100, description='Max jobs to return'),
):
    jobs = supabase_service.search_jobs(
        query=query,
        keyword=keyword,
        time_frame=time_frame,
        limit=limit
    )
    return {'jobs': jobs, 'count': len(jobs)}


@router.get('/jobs/{job_id}')
def get_job(job_id: str):
    job = supabase_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f'Job {job_id} not found in Supabase database.')
    return job


@router.post('/recommend')
async def recommend_jobs(
    resume_file: UploadFile = File(...),
    category: str = Form('All'),
    query: str = Form(''),
    time_frame: str = Form('all'),
    experience_level: str = Form('all'),
    limit: int = Form(10),
):
    try:
        content = await resume_file.read()
        resume_text = resume_service.extract_text_from_file(content, resume_file.filename or 'resume')
        result = recommender_service.find_recommendations(
            resume_text=resume_text,
            category=category,
            query=query,
            time_frame=time_frame,
            experience_level=experience_level,
            limit=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

