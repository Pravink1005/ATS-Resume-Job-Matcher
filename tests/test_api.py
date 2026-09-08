from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_root(): assert client.get('/').status_code==200
def test_health():
    r=client.get('/health'); assert r.status_code==200 and r.json()['status']=='healthy'
def test_match_invalid_ids(): assert client.post('/match',json={'resume_id':999999,'job_id':999999}).status_code==404
