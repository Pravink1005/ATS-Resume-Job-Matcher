from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repository import ResumeRepository
from app.services.resume_service import ResumeService
from app.services.resume_health_service import ResumeHealthService
from app.services.resume_tailor_service import ResumeTailorService

router = APIRouter()
service = ResumeService()
health_service = ResumeHealthService()
tailor_service = ResumeTailorService()

@router.post('/resume/upload')
async def upload_resume(resume_file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        data = await resume_file.read()
        text = service.extract_text_from_file(data, resume_file.filename or '')
        x = ResumeRepository.create(db, resume_file.filename, text)
        return {'resume_id': x.id, 'filename': x.filename, 'resume_text': x.resume_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/resume/{resume_id}')
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    x = ResumeRepository.get_by_id(db, resume_id)
    if not x:
        raise HTTPException(status_code=404, detail='Resume not found')
    return {'resume_id': x.id, 'filename': x.filename, 'resume_text': x.resume_text}

@router.post('/resume/health')
async def check_resume_health(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None)
):
    text = ''
    filename = ''
    if resume_file:
        data = await resume_file.read()
        filename = resume_file.filename or ''
        text = service.extract_text_from_file(data, filename)
    elif resume_text:
        text = resume_text
    else:
        raise HTTPException(status_code=400, detail='Either resume_file or resume_text must be provided.')

    return health_service.audit(text, filename)

@router.post('/resume/tailor')
async def tailor_resume(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None),
    job_description: str = Form(...)
):
    text = ''
    if resume_file:
        data = await resume_file.read()
        text = service.extract_text_from_file(data, resume_file.filename or '')
    elif resume_text:
        text = resume_text
    else:
        raise HTTPException(status_code=400, detail='Either resume_file or resume_text must be provided.')

    return tailor_service.generate_tailored_recommendations(text, job_description)

