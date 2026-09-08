from sqlalchemy import Column,Integer,Text,String,DateTime
from sqlalchemy.sql import func
from app.database.database import Base
class Job(Base):
    __tablename__='jobs'; id=Column(Integer,primary_key=True); job_title=Column(String(255),nullable=False); job_description=Column(Text,nullable=False); created_at=Column(DateTime(timezone=True),server_default=func.now())
