from fastapi import APIRouter,Depends,File,HTTPException,UploadFile
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import ResumeRepository
from app.services.resume_service import ResumeService
router=APIRouter(); service=ResumeService()
@router.post('/resume/upload')
async def upload_resume(resume_file:UploadFile=File(...),db:Session=Depends(get_db)):
    try:
        data=await resume_file.read(); text=service.extract_text_from_file(data,resume_file.filename or '')
        x=ResumeRepository.create(db,resume_file.filename,text); return {'resume_id':x.id,'filename':x.filename,'resume_text':x.resume_text}
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))
@router.get('/resume/{resume_id}')
def get_resume(resume_id:int,db:Session=Depends(get_db)):
    x=ResumeRepository.get_by_id(db,resume_id)
    if not x: raise HTTPException(status_code=404,detail='Resume not found')
    return {'resume_id':x.id,'filename':x.filename,'resume_text':x.resume_text}
