from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import JobRepository
from app.schemas.job_schema import JobCreate
from app.services.job_service import JobService
router=APIRouter(); service=JobService()
@router.post('/job')
def create_job(req:JobCreate,db:Session=Depends(get_db)):
    try:
        p=service.parse(req.job_description); x=JobRepository.create(db,p['job_title'] or req.job_title,req.job_description); return {'job_id':x.id,'job_title':x.job_title,'job_description':x.job_description}
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))
@router.get('/job/{job_id}')
def get_job(job_id:int,db:Session=Depends(get_db)):
    x=JobRepository.get_by_id(db,job_id)
    if not x: raise HTTPException(status_code=404,detail='Job not found')
    return {'job_id':x.id,'job_title':x.job_title,'job_description':x.job_description}
