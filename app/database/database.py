from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

BASE = Path(__file__).resolve().parents[2]
(BASE / 'data').mkdir(exist_ok=True)

url = settings.database_url
if url.startswith('sqlite:///./'):
    url = 'sqlite:///' + str((BASE / url.replace('sqlite:///./', '')).resolve())

engine = create_engine(
    url,
    connect_args={'check_same_thread': False} if url.startswith('sqlite') else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def init_db():
    Base.metadata.create_all(bind=engine)
    # Automatically add missing columns in SQLite if tables existed prior to v3.1 update
    try:
        inspector = inspect(engine)
        if 'match_results' in inspector.get_table_names():
            existing_columns = {col['name'] for col in inspector.get_columns('match_results')}
            with engine.begin() as conn:
                for col in ['requirement_analysis', 'context_match', 'weighted_scores']:
                    if col not in existing_columns:
                        conn.execute(text(f'ALTER TABLE match_results ADD COLUMN {col} TEXT'))
    except Exception:
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
