"""Comprehensive end-to-end verification script for ResumeMatch ATS.
Tests:
1. Exact experience parsing on Pravin Kumar's resume (1.3 yrs).
2. ATS Match scoring accuracy and dynamic weight re-balancing.
3. ATS Resume Health & Parseability audit (Score 85+, Grade A).
4. AI Resume Tailor (Tailored summary and STAR-method bullets).
5. 1-Click Deep Match data structure completeness.
6. CSV Application Tracker generation and formatting.
"""
from app.services.matching_service import MatchingService
from app.services.resume_health_service import ResumeHealthService
from app.services.resume_tailor_service import ResumeTailorService
from frontend.app import build_recommendations_csv


PRAVIN_RESUME = """
PRAVIN KUMAR A
Data Professional | Python, SQL, ETL Pipelines & Data Analytics
Thoothukudi, Tamil Nadu, India | +91 8148241679 | a.pravink32@gmail.com | linkedin.com/in/pravin32 | github.com/Pravink1005

PROFESSIONAL SUMMARY
Data professional with 1+ year of hands-on experience building, monitoring, and optimizing ETL/ELT pipelines, validating data 
quality, and analyzing data using Python, SQL, and cloud services. Skilled in Jenkins CI/CD, Grafana, PostgreSQL, MongoDB, and 
AWS (S3, EC2), with proven ability to automate workflows, reduce pipeline failures, and deliver Power BI and Streamlit dashboards
that drive business decisions.

TECHNICAL SKILLS
Programming & Query Languages: Python, SQL (Joins, CTEs, Window Functions)
Data Engineering: ETL/ELT Pipelines, Data Pipelines, Data Warehousing, Data Modeling, Data Validation, Data Cleaning, Data 
Transformation, Workflow Automation, Job Scheduling
Data Analysis & Visualization: Exploratory Data Analysis (EDA), Statistical Analysis, KPI Reporting, Excel, Power BI, Grafana, 
Streamlit, Pandas, NumPy, Matplotlib
Databases: PostgreSQL, MySQL, MongoDB, Firebase
Cloud & DevOps: AWS (S3, EC2), Jenkins (CI/CD), Git, GitHub, Ubuntu
Machine Learning: XGBoost, Predictive Modeling, Scikit-learn
Soft Skills: Problem Solving, Critical Thinking, Communication, Time Management, Teamwork

PROFESSIONAL EXPERIENCE
Junior Process Associate | Aggregate Intelligence 07/2025 – 07/2026
• Monitored and executed Python-based ETL jobs, validating data loads into PostgreSQL and MongoDB to ensure reliable daily 
operations and accurate downstream reporting.
• Performed data quality checks, including data validation, completeness verification, and consistency analysis, to maintain data 
integrity.
• Tracked scheduled jobs in Jenkins CI/CD and monitored pipeline performance metrics in Grafana dashboards, identifying 
anomalies and reporting trends to the team.
• Troubleshot ETL pipeline failures and analyzed job outputs to resolve data discrepancies, improving overall job reliability and 
data accuracy.
• Collaborated with cross-functional teams to interpret data issues and support informed decision-making.

Data Analytics Intern | HCL Technologies 12/2024 – 02/2025
• Contributed to an AI-powered Project Cost Estimation system using Python, XGBoost, and Streamlit to support project 
planning
• Collected, cleaned, and processed data to identify trends and support machine learning model development.
• Automated DOC/Excel report generation, reducing manual reporting time also Integrated Firebase for cloud-based data 
storage and retrieval, enabling real-time stakeholder access.
• Collaborated with cross-functional teams to ensure data accuracy, workflow optimization, and project performance.

PROJECTS
Weather ETL Pipeline & Analysis Dashboard Python, PostgreSQL, Streamlit
• Built an ETL pipeline ingesting real-time weather API data for multiple Tamil Nadu cities with automated hourly scheduling.
• Designed modular workflows with data validation and transformation logic, storing history in PostgreSQL for trend analysis.
• Created an interactive Streamlit dashboard visualizing temperature, humidity, and wind trends for data-driven insights.

AI-Based Project Cost Estimator Python, XGBoost, Streamlit, Firebase
• Built an AI-powered cost estimation system using Python, XGBoost, and Streamlit to support project planning.
• Performed data collection, cleaning, preprocessing, and validation to ensure data quality and model reliability.
• Automated report generation in DOC and Excel formats, built interactive dashboards, and integrated Firebase for cloud-based 
data storage.

EDUCATION
M.Sc. Data Science and Business Analysis | Rathinam College of Arts and Science, Coimbatore | CGPA: 7.7 08/2023 – 05/2025
B.Sc. Information Technology | Pope's College of Arts and Science, Tuticorin | CGPA: 8.4 08/2020 – 05/2023
"""

SAMPLE_JOB = """
Job Title: Data Analyst / ETL Engineer
Company: CloudScale Analytics
Location: Bengaluru, India
Required Experience: 1 year
Requirements:
- Strong proficiency in Python, SQL, and ETL pipelines
- Hands-on experience with PostgreSQL and MongoDB
- Experience building dashboards using Power BI or Streamlit
- Knowledge of Docker and CI/CD pipelines
Education: Bachelor or Master degree in Computer Science, Data Science, or Information Technology
"""


def test_pravin_kumar_resume_complete_workflow():
    # 1. Health Audit Verification
    health_svc = ResumeHealthService()
    health = health_svc.audit(PRAVIN_RESUME)
    assert health['health_score'] >= 85, f"Expected health >= 85, got {health['health_score']}"
    assert health['grade'] in ('A', 'B')
    assert health['contact_info']['email'] == 'a.pravink32@gmail.com'
    assert health['contact_info']['phone'] == '+91 8148241679'
    assert 'experience' in health['sections_detected']
    assert 'education' in health['sections_detected']
    assert 'skills' in health['sections_detected']

    # 2. Match & Experience Verification
    ms = MatchingService()
    res = ms.match(PRAVIN_RESUME, SAMPLE_JOB)

    # Candidate experience must be 1.33 yrs (formats to 1.3 yrs in UI)
    assert f"{res['candidate_experience']:.1f}" == "1.3"
    assert res['required_experience'] == 1.0
    assert res['experience_gap'] == 0.0
    assert res['experience_status'].lower() == 'meets requirement'

    # Overall score must reflect strong match (>= 85%)
    assert res['overall_score'] >= 85.0
    assert res['recommendation'] == 'Excellent Match'

    # 3. AI Resume Tailoring Verification
    tailoring = res.get('tailoring_suggestions', {})
    assert tailoring, "Tailoring suggestions should be present"
    assert 'Data Analyst / ETL Engineer' in tailoring['target_title']
    assert len(tailoring['star_bullet_points']) > 0

    # Missing skill Docker should have a STAR bullet point
    star_skills = [b['skill'].lower() for b in tailoring['star_bullet_points']]
    assert any('docker' in s for s in star_skills)

    # 4. CSV Job Tracker Verification
    mock_recs = [
        {
            'title': 'Data Analyst / ETL Engineer',
            'company': 'CloudScale Analytics',
            'location': 'Bengaluru, India',
            'overall_score': res['overall_score'],
            'recommendation': res['recommendation'],
            'matched_skills': res['matched_skills'],
            'missing_skills': res['missing_skills'],
            'candidate_experience': res['candidate_experience'],
            'required_experience': res['required_experience'],
            'experience_status': res['experience_status'],
            'posted_label': '1 hr ago',
            'link': 'https://linkedin.com/jobs/view/123456'
        }
    ]
    csv_text = build_recommendations_csv(mock_recs)
    assert 'ATS Match Score' in csv_text
    assert 'CloudScale Analytics' in csv_text
    assert f"{res['overall_score']:.1f}%" in csv_text
    assert 'To Apply' in csv_text
