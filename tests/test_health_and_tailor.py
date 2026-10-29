from fastapi.testclient import TestClient
from app.main import app
from app.services.resume_health_service import ResumeHealthService
from app.services.resume_tailor_service import ResumeTailorService


client = TestClient(app)


def test_resume_health_service_complete_resume():
    service = ResumeHealthService()
    resume_text = """
    Jane Doe
    jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe | github.com/janedoe
    
    Professional Summary
    Results-driven Software Engineer with 5+ years of experience in distributed systems.
    
    Work Experience
    Senior Software Engineer | Tech Corp (2021 - Present)
    - Architected and engineered high-throughput REST APIs using Python and FastAPI, reducing latency by 45%.
    - Spearheaded microservices migration, orchestrating deployments on Kubernetes for 500k+ daily active users.
    - Optimized PostgreSQL database queries with custom indexing, cutting server costs by $35,000 annually.
    - Mentored a distributed team of 6 engineers and streamlined CI/CD pipeline deployments.
    
    Education
    Bachelor of Science in Computer Science, State University
    
    Skills
    Python, FastAPI, Kubernetes, Docker, PostgreSQL, CI/CD, Git
    """
    audit = service.audit(resume_text, "resume.pdf")

    assert audit['health_score'] >= 85
    assert audit['grade'] in ('A', 'B')
    assert audit['contact_info']['email'] == 'jane.doe@example.com'
    assert 'experience' in audit['sections_detected']
    assert 'education' in audit['sections_detected']
    assert 'skills' in audit['sections_detected']
    assert len(audit['metrics_found']) >= 3
    assert len(audit['action_verbs_found']) >= 4
    assert len(audit['checklist']['critical']) == 0
    assert any('Email detected' in item for item in audit['checklist']['passed'])


def test_resume_health_service_poor_resume():
    service = ResumeHealthService()
    # Missing contact info, missing section headers, passive voice, zero metrics
    poor_text = """
    John Doe
    I like coding.
    Was part of a team and helped with some coding tasks.
    Responsible for bug fixing and worked with python sometimes.
    """
    audit = service.audit(poor_text)

    assert audit['health_score'] < 50
    assert audit['grade'] in ('C', 'D')
    assert 'email' not in audit['contact_info']
    assert len(audit['checklist']['critical']) >= 2
    assert any('responsible for' in p for p in audit['weak_phrases_found'])


def test_resume_tailor_service():
    service = ResumeTailorService()
    resume_text = """
    Jane Doe
    jane.doe@example.com
    Experience: 4 years
    Skills: Python, SQL
    """
    job_desc = """
    Job Title: Senior Backend Engineer
    Required: Python, Docker, FastAPI, Kubernetes, PostgreSQL
    Experience: 3 years
    """
    tailored = service.generate_tailored_recommendations(resume_text, job_desc)

    assert 'Senior Backend Engineer' in tailored['target_title']
    assert 'Senior Backend Engineer' in tailored['tailored_summary']
    assert len(tailored['star_bullet_points']) > 0

    # Ensure missing skills (Docker, FastAPI, Kubernetes, PostgreSQL) have STAR bullets
    star_skills = [b['skill'].lower() for b in tailored['star_bullet_points']]
    assert any('docker' in s for s in star_skills)
    assert any('fastapi' in s for s in star_skills)

    # Check formatted copy paste skills
    assert 'Core Technologies' in tailored['skills_section']['formatted_copy_paste']
    assert len(tailored['placement_strategy']) >= 2


def test_api_resume_health_endpoint():
    resume_text = """
    Alice Smith | alice@gmail.com | 123-456-7890 | linkedin.com/in/alicesmith
    Experience
    - Developed backend systems in Go.
    Education
    - B.S. in Computer Science
    Skills
    - Go, Docker
    """
    response = client.post("/resume/health", data={"resume_text": resume_text})
    assert response.status_code == 200
    data = response.json()
    assert 'health_score' in data
    assert data['contact_info']['email'] == 'alice@gmail.com'


def test_api_resume_tailor_endpoint():
    resume_text = "Software Engineer\nSkills: Python, SQL\nExperience: 3 years"
    job_desc = "Job Title: Cloud Engineer\nRequired: Python, AWS, Docker\nExperience: 2 years"
    response = client.post("/resume/tailor", data={
        "resume_text": resume_text,
        "job_description": job_desc
    })
    assert response.status_code == 200
    data = response.json()
    assert 'tailored_summary' in data
    assert 'star_bullet_points' in data
    assert len(data['star_bullet_points']) >= 2
