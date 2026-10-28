from io import BytesIO
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    assert client.get('/').status_code == 200

def test_health():
    r = client.get('/health')
    assert r.status_code == 200 and r.json()['status'] == 'healthy'

def test_match_invalid_ids():
    assert client.post('/match', json={'resume_id': 999999, 'job_id': 999999}).status_code == 404

def test_match_file_and_persistence():
    resume_content = b"Data Analyst with 3 years experience in Python, SQL, Excel, and Power BI. Bachelor degree in Computer Science."
    job_desc = "Role: Senior Data Analyst\nRequired: Python, SQL, Power BI\nExperience: 2+ years\nBachelor degree in Computer Science"

    response = client.post(
        '/match/file',
        files={'resume_file': ('my_resume.txt', BytesIO(resume_content), 'text/plain')},
        data={'job_description': job_desc}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'match_id' in data
    assert 'overall_score' in data
    assert 'recommendation' in data
    assert 'requirement_analysis' in data
    assert len(data['requirement_analysis']) > 0
    assert 'context_match' in data
    assert 'weighted_scores' in data

    # Verify retrieval preserves all detailed fields
    match_id = data['match_id']
    get_res = client.get(f'/match/{match_id}')
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved['match_id'] == match_id
    assert len(retrieved['requirement_analysis']) == len(data['requirement_analysis'])
    assert retrieved['context_match'] == data['context_match']
    assert retrieved['weighted_scores'] == data['weighted_scores']

def test_supabase_endpoints():
    res = client.get('/supabase/status')
    assert res.status_code == 200
    data = res.json()
    assert 'configured' in data
    assert 'connected' in data

    kw_res = client.get('/supabase/keywords')
    assert kw_res.status_code == 200
    assert 'keywords' in kw_res.json()

    jobs_res = client.get('/supabase/jobs?limit=3')
    assert jobs_res.status_code == 200
    assert 'jobs' in jobs_res.json()

def test_recommend_jobs_endpoint():
    resume_content = b"Data Analyst with 3 years experience in Python, SQL, Excel, and Power BI."
    res = client.post(
        '/supabase/recommend',
        files={'resume_file': ('analyst_resume.txt', BytesIO(resume_content), 'text/plain')},
        data={'category': 'Data Analyst', 'time_frame': 'all', 'experience_level': 'all', 'limit': 3}
    )
    assert res.status_code == 200
    data = res.json()
    assert 'recommendations' in data
    assert 'total_scanned' in data
    assert len(data['recommendations']) > 0
    top = data['recommendations'][0]
    assert 'overall_score' in top
    assert 'title' in top
    assert 'company' in top
    assert 'link' in top
    assert 'posted_label' in top
