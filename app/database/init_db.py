from app.database.database import Base,engine
from app.models import Resume,Job,MatchResult
if __name__=='__main__': Base.metadata.create_all(bind=engine); print('Database initialized.')
