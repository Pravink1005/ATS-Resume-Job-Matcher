from app.database.database import init_db
from app.models import Resume, Job, MatchResult

if __name__ == '__main__':
    init_db()
    print('Database initialized.')
