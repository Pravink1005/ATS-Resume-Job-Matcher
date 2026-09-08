from sqlalchemy import Column,Integer,Text,String,DateTime
from sqlalchemy.sql import func
from app.database.database import Base
class Resume(Base):
    __tablename__='resumes'; id=Column(Integer,primary_key=True); filename=Column(String(255),nullable=False); resume_text=Column(Text,nullable=False); created_at=Column(DateTime(timezone=True),server_default=func.now())
