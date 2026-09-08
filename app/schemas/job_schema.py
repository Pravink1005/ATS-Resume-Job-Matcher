from pydantic import BaseModel
class JobCreate(BaseModel): job_title:str; job_description:str
class JobResponse(BaseModel): job_id:int; job_title:str; job_description:str
