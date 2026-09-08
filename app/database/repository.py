import json
from app.models import Resume,Job,MatchResult
class ResumeRepository:
    @staticmethod
    def create(db,filename,resume_text):
        x=Resume(filename=filename,resume_text=resume_text); db.add(x); db.commit(); db.refresh(x); return x
    @staticmethod
    def get_by_id(db,resume_id): return db.get(Resume,resume_id)
class JobRepository:
    @staticmethod
    def create(db,job_title,job_description):
        x=Job(job_title=job_title,job_description=job_description); db.add(x); db.commit(); db.refresh(x); return x
    @staticmethod
    def get_by_id(db,job_id): return db.get(Job,job_id)
class MatchRepository:
    @staticmethod
    def create(db,data):
        payload=dict(data)
        for k,v in list(payload.items()):
            if isinstance(v,(list,dict)): payload[k]=json.dumps(v)
        x=MatchResult(**payload); db.add(x); db.commit(); db.refresh(x); return x
    @staticmethod
    def get_by_id(db,match_id): return db.get(MatchResult,match_id)

def decode(v):
    if v is None:return []
    try:return json.loads(v)
    except Exception:return v
