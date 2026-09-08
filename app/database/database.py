from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import settings
BASE=Path(__file__).resolve().parents[2]; (BASE/'data').mkdir(exist_ok=True)
url=settings.database_url
if url.startswith('sqlite:///./'): url='sqlite:///'+str((BASE/url.replace('sqlite:///./','')).resolve())
engine=create_engine(url,connect_args={'check_same_thread':False} if url.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
