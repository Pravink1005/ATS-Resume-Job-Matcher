from pydantic import BaseModel
class ResumeUploadResponse(BaseModel): resume_id:int; filename:str; resume_text:str
class ResumeResponse(BaseModel): resume_id:int; filename:str; resume_text:str
