# Resume Job Matcher — Full Updated Project

## Features
- One-resume Streamlit workflow
- No configuration/sidebar panel
- PDF, DOCX and TXT resume parsing
- Explainable skill matching: exact, alias, partial and related
- Experience gap scoring
- Education relevance check
- Competency and keyword matching
- TF-IDF similarity
- SQLite persistence
- FastAPI API + Swagger docs
- Docker-ready

## Run on Windows PowerShell
```powershell
cd D:\resume_job_matcher
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.database.init_db
pytest -v
uvicorn app.main:app --reload
```
Open another PowerShell:
```powershell
cd D:\resume_job_matcher
.\.venv\Scripts\Activate.ps1
streamlit run frontend\app.py
```
Frontend: http://127.0.0.1:8501
API docs: http://127.0.0.1:8000/docs

## Important scoring behavior
A JD saying `2+ years preferred` is not treated as an automatic rejection. The engine reports the experience gap and scores the experience component proportionally. Exact skills are stronger evidence than related skills, so the score is not artificially inflated by broad keyword overlap.
