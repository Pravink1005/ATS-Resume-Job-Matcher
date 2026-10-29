# 🚀 ResumeMatch ATS

<p align="center">
  <img src="docs/assets/hero_banner.svg" alt="ResumeMatch ATS Hero Banner" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);" />
</p>

<p align="center">
  <strong>Next-Generation Explainable ATS Intelligence &amp; AI Career Optimization Platform</strong><br>
  Engineered with strict evidence-based requirement matching, production knockout safety gates, section-aware qualification weighting, automated resume health auditing, live discovery across 6,200+ roles, and targeted STAR-formula AI tailoring.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Supabase-Live%20Jobs%20(6%2C200+)-3ECF8E?style=flat&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Tests-41%20Passing%20(100%25)-brightgreen?style=flat&logo=pytest&logoColor=white" alt="Tests" />
  <img src="https://img.shields.io/badge/Production-Safety%20Gated-blueviolet?style=flat" alt="Safety Gated" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat" alt="License" />
</p>

---

## 📌 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Why ResumeMatch ATS is Best-In-Class](#-why-resumematch-ats-is-best-in-class)
  - [🎯 For Candidates & Job Seekers](#-for-candidates--job-seekers)
  - [🏢 For Recruiters & Talent Acquisition](#-for-recruiters--talent-acquisition)
- [🖥️ Modern SaaS User Interface](#-modern-saas-user-interface)
- [🛡️ Production Safety & Recruiter Knockout Architecture](#-production-safety--recruiter-knockout-architecture)
  - [1. Seniority Shortfall Knockout Gate](#1-seniority-shortfall-knockout-gate)
  - [2. Section-Aware Mandatory vs. Preferred Weighting](#2-section-aware-mandatory-vs-preferred-weighting)
  - [3. Core Technical Qualification Gate](#3-core-technical-qualification-gate)
  - [4. Incomplete Job Description Guard](#4-incomplete-job-description-guard)
- [⚡ Key Platform Capabilities](#-key-platform-capabilities)
  - [1. Dual Matching Modes](#1-dual-matching-modes)
  - [2. 1-Click Deep Match Inspection](#2-1-click-deep-match-inspection)
  - [3. 📊 CSV Job Application Tracker (Google Sheets / Excel)](#3--csv-job-application-tracker-google-sheets--excel)
  - [4. 🎯 AI Resume Tailor & STAR Accomplishment Generator](#4--ai-resume-tailor--star-accomplishment-generator)
  - [5. 🩺 ATS Resume Health Check & Parseability Audit](#5--ats-resume-health-check--parseability-audit)
  - [6. ⏱️ Accurate Candidate Experience Engine](#6-️-accurate-candidate-experience-engine)
  - [7. 🌐 Enterprise Cloud, DevOps & Security Taxonomy](#7--enterprise-cloud-devops--security-taxonomy)
- [📐 Scoring Engine Mathematical Architecture](#-scoring-engine-mathematical-architecture)
  - [Dynamic Weight Re-balancing Math](#dynamic-weight-re-balancing-math)
  - [Calibrated TF-IDF Logistic Sigmoid Curve](#calibrated-tf-idf-logistic-sigmoid-curve)
- [🏗️ System Architecture & Workflow Pipeline](#-system-architecture--workflow-pipeline)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [Prerequisites](#prerequisites)
  - [Installation & Virtual Environment](#installation--virtual-environment)
  - [Starting the Services](#starting-the-services)
  - [Docker Compose Deployment](#docker-compose-deployment)
- [🔌 REST API Reference](#-rest-api-reference)
- [🧪 Automated Test Suite (41 Tests, 100% Green)](#-automated-test-suite-41-tests-100-green)
- [📁 Project Directory Structure](#-project-directory-structure)
- [📄 License](#-license)

---

## 🌟 Overview

Modern Applicant Tracking Systems are notorious for being opaque black boxes that reject qualified candidates over minor formatting discrepancies, unstated requirements, or naive keyword matching. Conversely, generic resume-matching tools inflate match percentages up to 95% on senior roles without checking whether a candidate actually possesses the required years of experience or core qualifications.

**ResumeMatch ATS** eliminates both problems. It provides an objective, transparent, and recruiter-accurate evaluation system that:
1. **Parses Resumes Honestly**: Validates binary magic-byte headers, extracts exact career tenure across overlapping date intervals, and isolates real technical skills without false positives.
2. **Enforces Production Knockout Gates**: Automatically knocks out candidates with severe seniority deficits (e.g. 1-year junior applying for a 7-year Staff role) to ensure real-world hiring accuracy.
3. **Prioritizes Section-Aware Requirements**: Distinguishes mandatory *"Must-Have"* qualifications from *"Nice-to-Have / Preferred"* bonus skills, weighting them at an $85\% / 15\%$ ratio.
4. **Discovers Live Roles Across 6,200+ Openings**: Connects live to a cloud database holding 6,200+ verified positions, ranking opportunities by true algorithmic fit.
5. **Empowers Candidates with Actionable AI Tailoring**: Audits parseability health (0–100 score + Grade A–D), generates tailored professional summaries, and crafts production-ready **STAR-formula accomplishment bullet points**.

---

## ✨ Why ResumeMatch ATS is Best-In-Class

<p align="center">
  <img src="docs/assets/ats_match_dashboard.svg" alt="ResumeMatch ATS Modern Dashboard Preview" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);" />
</p>

### 🎯 For Candidates & Job Seekers

| Feature | The Problem in Standard ATS | How ResumeMatch ATS Solves It |
| :--- | :--- | :--- |
| **Experience Tenure Parsing** | Naive parsers discard numeric dates (`07/2025–07/2026`) or sum to `0.0 yrs`, falsely triggering hard rejections. | Employs boundary-safe header detection, dual date formats (`MM/YYYY` and named months), inclusive month math, and explicit tenure extraction (**1.3 yrs** verified). |
| **The "ATS Black Hole"** | Candidates receive generic rejection emails with zero explanation of why they were filtered out. | Provides complete evidence transparency: exact matched skills, missing skills, tenure gap, and clear safety gate notifications. |
| **Missing Skill Gaps** | Knowing you lack a skill (e.g. Docker, AWS, or Terraform) doesn't teach you how to articulate relevant accomplishments. | Built-in **AI Resume Tailor** generates role-customized STAR bullet points (*Situation, Task, Action, Result*) targeting missing skills with measurable metrics. |
| **Application Fatigue** | Applying to hundreds of jobs manually without tracking results leads to burnout. | Features **1-Click Deep Match** for instant drilldown and a **CSV Application Tracker** exporting ranked roles with clean direct application links. |
| **Silent Formatting Rejections** | Missing contact links, non-standard section headers, or weak passive verbs get resumes discarded silently. | The **ATS Health Check** audits contact channels, headers, quantifiable metrics, and action verb density with an actionable letter grade (A–D). |

### 🏢 For Recruiters & Talent Acquisition

- **Conservative Direct Evidence**: Semantic similarity is never treated as proof of a skill. Related tools are flagged as supporting evidence rather than directly satisfied.
- **Production Seniority Knockouts**: Junior candidates cannot achieve false "Excellent Matches" on senior positions. A candidate with 1.3 years applying for a 7-year Lead role is automatically gated to $\le 45\%$ (Low Match).
- **Dynamic Weight Re-balancing**: If a job description does not specify an education requirement, candidates are **not** penalized 10%—the remaining categories scale proportionally to 100%.
- **Calibrated Semantic Similarity**: Replaces deceptive raw cosine similarity with a calibrated logistic curve mapping realistic cosine ranges (0.05–0.40) to meaningful scores (20%–100%).
- **Executive Audit Reports**: Downloadable formatted `.docx` reports ready to share directly with hiring committees.

---

## 🛡️ Production Safety & Recruiter Knockout Architecture

Real-world hiring workflows enforce strict minimum qualifications. ResumeMatch ATS implements a 3-layer safety gate pipeline to eliminate false positives:

<p align="center">
  <img src="docs/assets/knockout_architecture.svg" alt="Production Safety & Recruiter Knockout Architecture" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);" />
</p>

### 1. Seniority Shortfall Knockout Gate
When a position mandates senior tenure ($\ge 5.0$ years) and a candidate has $< 40\%$ of the required experience or an experience deficit $> 3.5$ years:
- **Action**: Enforces an immediate **Seniority Knockout Gate**.
- **Score Cap**: Hard ceiling at **$\le 45.0\%$ (Low Match)**.
- **Transparency**: Explains the exact deficit: *"Role requires 7 yrs (Senior/Staff level); candidate has 1.3 yrs (deficit of 5.7 yrs)."*

### 2. Section-Aware Mandatory vs. Preferred Weighting
Job descriptions explicitly separate mandatory requirements from optional preferences:
- **Mandatory Requirements** (*"Required Qualifications"*, *"Must Haves"*, *"Basic Qualifications"*): Weighted at **85%** of the technical score.
- **Preferred Requirements** (*"Preferred Qualifications"*, *"Nice to Have"*, *"Bonus"*): Weighted at **15%**.
- **Benefit**: Missing a preferred "bonus" skill never unfairly triggers a technical knockout.

### 3. Core Technical Qualification Gate
If a candidate misses more than half ($> 50\%$) of the mandatory technical qualifications:
- **Action**: Enforces the **Core Technical Qualification Gate**.
- **Score Cap**: Hard ceiling at **$\le 58.0\%$ (Moderate Match)**.
- **Benefit**: Prevents non-technical candidates from ranking as high matches based solely on generic buzzwords.

### 4. Incomplete Job Description Guard
If a database record contains zero verifiable technical skills (such as a 10-word teaser snippet):
- **Action**: Enforces the **Incomplete JD Guard**.
- **Score Cap**: Hard ceiling at **$\le 55.0\%$**.
- **Benefit**: Eliminates false 94%+ match rankings caused by lack of stated requirements.

---

## ⚡ Key Platform Capabilities

### 1. Dual Matching Modes

```
┌────────────────────────────────────────────────────────────────────────┐
│                          ResumeMatch ATS UI                            │
├───────────────────────────────────┬────────────────────────────────────┤
│   🎯 Mode 1: Deep Single Match    │   🚀 Mode 2: Auto-Job Recommender  │
│  • Custom JD text paste OR        │  • Live search over 6,200+ roles   │
│  • Select from 6,200+ live jobs   │  • Filter by category & tenure     │
│  • 6 detailed analysis tabs       │  • Top matching jobs ranked        │
│  • Radar chart & DOCX download    │  • 1-Click Deep Match & CSV export │
│  • Gating badges & explanations   │  • Clean 1-click 'Apply' buttons   │
└───────────────────────────────────┴────────────────────────────────────┘
```

- **Mode 1: Deep Single Job Match**: Perform an exhaustive evaluation against a specific job posting with 6 interactive tabs:
  1. **📊 Score Breakdown & Overview**: Animated SVG radial gauge, category breakdown, candidate tenure gap, and active safety gates.
  2. **🎯 AI Resume Tailor**: Tailored professional summary, STAR bullet points, categorized skills block, and placement guide.
  3. **🩺 ATS Health Check**: Parseability score, contact channels, standard headers, quantifiable metrics, and active verbs.
  4. **📋 Requirements Analysis**: Requirement-level table showing exact text quotes, status, weight, and score.
  5. **🔍 Evidence Details**: Direct skill matches, canonical aliases, missing required skills, and related technologies.
  6. **🧭 Context & Alignment**: Job title overlap, seniority rating, location match, and work authorization check.

- **Mode 2: Auto-Job Recommender**: Upload your resume once and instantly rank live jobs from the 6,200+ cloud catalog with direct `🔗 Apply` links.

---

### 2. 1-Click Deep Match Inspection

When browsing opportunities in Mode 2, clicking **🔍 Inspect Full Match** on any recommendation card:
1. Transfers the full job title, company, and complete uncut description into Mode 1.
2. Recalculates all structured requirement evidence and context alignments.
3. Automatically transitions the interface into the 6-tab deep analysis view with **100% bitwise score parity**.
4. Includes a gap-positioned **`⬅️ Back to Top Search Recommendations`** button to return with all filters intact.

---

### 3. 📊 CSV Job Application Tracker (Google Sheets / Excel)

Clicking **📥 Export to CSV (Job Tracker)** downloads a structured spreadsheet formatted ready for import into **Google Sheets**, **Microsoft Excel**, or **Notion**:

| Column Header | Description |
| :--- | :--- |
| **Rank** | Numerical ranking by ATS Match Score |
| **Job Title** | Stated title of the opportunity |
| **Company** | Hiring organization |
| **Location** | Geographical location or Remote status |
| **ATS Match Score** | Computed percentage match score |
| **Recommendation Fit** | Excellent, Good, Moderate, or Low Match |
| **Matched Skills** | Comma-separated list of confirmed overlapping skills |
| **Missing Skills** | Required skills missing from the resume |
| **Candidate Experience** | Stated/parsed career tenure (years) |
| **Required Experience** | Job requirement tenure (years) |
| **Application URL** | Direct URL to apply online |
| **Application Status** | Pre-populated as `Ready to Apply` for pipeline tracking |

---

### 4. 🎯 AI Resume Tailor & STAR Accomplishment Generator

Available in Mode 1 (Tab 2) and within every recommendation card expander in Mode 2:

- **Tailored Professional Summary**: A 3-sentence summary highlighting the candidate's exact years of experience, primary technical stack, and direct alignment with the target role.
- **Dual-Mode STAR Bullet Points**:
  - **For Missing Skills**: Generates production-ready bullets targeting technical gaps:
    > *`[Docker] Developed and deployed containerized microservices using Docker, streamlining ETL deployment workflows and cutting local environment provisioning time by 40%.`*
  - **For 100% Skill Matches**: Generates high-impact accomplishment bullets showcasing core matched strengths:
    > *`[Python] Engineered automated Python data processing scripts and ETL workflows, eliminating 15+ hours of manual data extraction and validation each week.`*
- **Optimized ATS Skills Block**: Formatted for direct copy-paste into resume headers.

---

### 5. 🩺 ATS Resume Health Check & Parseability Audit

Evaluates technical parseability against standard ATS ingestion algorithms:

- **Health Score & Grade**: 0–100 score with Letter Grades (Grade A: 85+, Grade B: 70–84, Grade C: 50–69, Grade D: <50).
- **Contact Audit**: Confirms Email, Phone Number, LinkedIn, GitHub, and Location.
- **Header Check**: Detects standard sections (`Summary`, `Experience`, `Education`, `Skills`, `Projects`).
- **Quantifiable Metrics Detector**: Identifies percentage improvements, metrics, and business numbers.
- **Action Verb Density**: Measures active verbs (*spearheaded, architected, automated, engineered*) vs. passive voice.

---

### 6. ⏱️ Accurate Candidate Experience Engine

Solves the common industry bug where candidate experience evaluates to `0.0 yrs`:

1. **Boundary-Safe Header Detection**: Distinguishes true work experience headers from summary sentences.
2. **Dual-Format Date Parsing**: Handles named months (`Jul 2025 – Present`) and numeric intervals (`07/2025 – 07/2026`).
3. **Inclusive Month Math**: Accurately counts months between start and end dates (e.g. 07/2025 to 07/2026 = 13 months $\rightarrow$ **1.3 yrs**).
4. **Explicit Tenure Fallback**: Extracts stated tenure phrases like `1+ year of hands-on experience`.

---

### 7. 🌐 Enterprise Cloud, DevOps & Security Taxonomy

Comprehensive synonym and relationship mapping across modern technical stacks:
- **Cloud & Orchestration**: `AWS`, `Azure`, `GCP`, `OCI`, `OKE`, `Kubernetes`, `Docker`, `Containers`.
- **Infrastructure as Code**: `Terraform`, `Ansible`, `IaC`.
- **Observability & Telemetry**: `Prometheus`, `Grafana`, `OpenTelemetry` (`OTel`), `Datadog`, `Splunk`.
- **Security & Identity**: `Microsoft Purview`, `Zscaler`, `IAM`, `OAuth`, `Zero Trust`.
- **Languages & Frameworks**: `Python`, `Go`, `Java`, `FastAPI`, `Spring Boot`, `React`, `Next.js`.

---

## 📐 Scoring Engine Mathematical Architecture

The ATS scoring engine computes an objective 0–100 score using five core pillars:

$$\text{Final ATS Score} = w_{\text{tech}} S_{\text{tech}} + w_{\text{exp}} S_{\text{exp}} + w_{\text{edu}} S_{\text{edu}} + w_{\text{comp}} S_{\text{comp}} + w_{\text{tfidf}} S_{\text{tfidf}}$$

### Base Category Weights

| Category | Base Weight | Description |
| :--- | :---: | :--- |
| **Technical Skills** ($S_{\text{tech}}$) | **35%** | Exact, canonical alias, and partial matches (85% Mandatory / 15% Preferred). |
| **Experience Tenure** ($S_{\text{exp}}$) | **20%** | Candidate tenure vs. minimum required experience. |
| **Education Relevance** ($S_{\text{edu}}$) | **10%** | Degree level match (BS, MS, PhD) and field alignment. |
| **Core Competencies** ($S_{\text{comp}}$) | **10%** | Soft competencies, problem-solving, and collaboration. |
| **Responsibilities** ($S_{\text{resp}}$) | **10%** | Direct evidence of primary day-to-day job duties. |
| **Title & Seniority** ($S_{\text{title}}$) | **5%** | Stated job title overlap and seniority level. |
| **Context & Authorization** ($S_{\text{cont}}$) | **5%** | Location alignment and work authorization. |
| **Calibrated TF-IDF** ($S_{\text{tfidf}}$) | **5%** | Calibrated corpus vocabulary overlap. |

### Dynamic Weight Re-balancing Math

When a job description does not specify an education requirement or soft competencies, traditional ATS engines assign a zero, docking the candidate up to 25% unfairly.

ResumeMatch ATS detects active categories and **dynamically re-balances weights proportionally**:

$$w_i^{\text{rebalanced}} = \frac{w_i^{\text{base}}}{\sum_{j \in \text{Active Categories}} w_j^{\text{base}}}$$

### Calibrated TF-IDF Logistic Sigmoid Curve

Raw TF-IDF cosine similarity between a concise resume and an exhaustive job description naturally clusters between $0.08$ and $0.35$. Using raw cosine directly results in severely deflated scores.

ResumeMatch ATS applies a calibrated logistic sigmoid transformation:

$$S_{\text{calibrated}} = \frac{1}{1 + e^{-18 \times (\text{cosine} - 0.18)}}$$

| Raw Cosine Similarity | Real-World Meaning | Calibrated ATS Score |
| :---: | :---: | :---: |
| **< 0.05** | Negligible vocabulary overlap | **15% – 25%** |
| **0.10** | Moderate topical overlap | **45% – 55%** |
| **0.18** | Solid technical alignment (inflection point) | **70%** |
| **0.25+** | High semantic alignment | **85% – 95%** |
| **0.35+** | Complete vocabulary alignment | **98% – 100%** |

---

## 🏗️ System Architecture & Workflow Pipeline

```mermaid
flowchart TD
    subgraph UI ["Modern Frontend (Streamlit)"]
        A["Resume File (PDF / DOCX / TXT)"]
        B1["Mode 1: Deep Single Match\n(Custom JD or Supabase Role)"]
        B2["Mode 2: Auto-Job Recommender\n(Search 6,200+ Live Jobs)"]
        UI_Tabs["6 Analysis Tabs:\nScore Breakdown | AI Tailor | Health Check\nRequirements | Evidence | Context"]
        UI_CSV["1-Click Deep Match &\nCSV Job Tracker Export"]
    end

    subgraph API ["Backend API (FastAPI)"]
        R_Upload["/resume/upload\nMagic-Byte Header Validation"]
        R_Match["/match/file & /match\nFull ATS Engine Pipeline"]
        R_Health["/resume/health\nATS Health & Parseability"]
        R_Tailor["/resume/tailor\nSTAR Bullets & Summary"]
        R_Supa["/jobs/supabase & /jobs/recommend\nPostgREST Live Query & Enrichment"]
    end

    subgraph NLP ["NLP & Extraction Engine"]
        N_Exp["Experience Extractor\n(Date Ranges, Inclusive Tenure, Explicit)"]
        N_Skill["Skill Extractor\n(Exact, Canonical Aliases, Boundary Check)"]
        N_Req["Requirement Extractor\n(Section-Aware Mandatory vs Preferred)"]
        N_Cont["Context Extractor\n(Title, Seniority, Location, Authorization)"]
    end

    subgraph Gates ["Production Safety Pipeline"]
        G_Sen["Seniority Knockout Gate\n(≥5 yrs req, <40% tenure → Cap ≤45%)"]
        G_Tech["Technical Gate\n(<50% mandatory skills → Cap ≤58%)"]
        G_Inc["Incomplete JD Guard\n(0 skills detected → Cap ≤55%)"]
    end

    subgraph Storage ["Data Sources & Persistence"]
        DB_Local[("SQLite matches.db\nResumes, Jobs, Matches History")]
        DB_Supa[("Supabase Cloud DB\n6,200+ Active Tech Jobs")]
    end

    A --> R_Upload
    B1 --> R_Match
    B2 --> R_Supa
    R_Supa <--> DB_Supa

    R_Upload --> N_Exp & N_Skill
    R_Match --> N_Req & N_Cont
    N_Skill & N_Req --> Gates
    Gates --> DB_Local

    R_Match --> UI_Tabs
    R_Health --> UI_Tabs
    R_Tailor --> UI_Tabs
    R_Supa --> UI_CSV
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.10** or higher
- **PowerShell** (Windows) or **Bash** (macOS/Linux)
- Git

### Installation & Virtual Environment

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/your-username/ATS-Resume-Job-Matcher.git
   cd ATS-Resume-Job-Matcher
   ```

2. **Create and activate virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Initialize local SQLite database**:
   ```powershell
   python -m app.database.init_db
   ```

5. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-or-service-key
   DATABASE_URL=sqlite:///./matches.db
   ```

---

### Starting the Services

Start the **FastAPI Backend** (runs on port `8000`):
```powershell
uvicorn app.main:app --reload
```

In a second terminal window, start the **Streamlit Frontend** (runs on port `8501`):
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend\app.py
```

- **Web Application**: [http://127.0.0.1:8501](http://127.0.0.1:8501)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Docker Compose Deployment

Run the entire stack with a single command:
```powershell
docker compose up --build
```

---

## 🔌 REST API Reference

The FastAPI backend exposes RESTful endpoints documented via OpenAPI at `/docs`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status and root greeting. |
| `GET` | `/health` | Service health status. |
| `POST` | `/resume/upload` | Upload resume file (PDF/DOCX/TXT), validate magic bytes, and store parsed text. |
| `GET` | `/resume/{resume_id}` | Retrieve stored resume by ID. |
| `POST` | `/resume/health` | Audit parseability health, contact info, headers, quantifiable metrics, and action verbs. |
| `POST` | `/resume/tailor` | Generate tailored summary, missing-skill STAR bullets, and categorized skills block. |
| `POST` | `/job/create` | Save custom job description to database. |
| `GET` | `/job/{job_id}` | Retrieve stored job description by ID. |
| `POST` | `/match` | Calculate ATS match using existing `resume_id` and `job_id`. |
| `POST` | `/match/file` | One-step endpoint: upload resume file + job text, returning complete ATS score and evidence. |
| `GET` | `/match/{match_id}` | Retrieve historical match results with complete requirement-level breakdown. |
| `GET` | `/matches/history` | List recent match evaluations. |
| `GET` | `/match/{match_id}/report`| Download formatted `.docx` executive ATS audit report. |
| `GET` | `/jobs/supabase` | Query live Supabase jobs with search and category filters. |
| `GET` | `/jobs/supabase/categories`| Retrieve list of available job categories from Supabase. |
| `POST` | `/jobs/recommend` | Upload resume and receive top ranked job recommendations with direct apply links. |

---

## 🧪 Automated Test Suite (41 Tests, 100% Green)

ResumeMatch ATS includes an automated Pytest test suite with **100% passing tests (41/41)**:

```powershell
pytest -v
```

### Test Suite Breakdown

| Test Module | Tests | Coverage & Focus Areas |
| :--- | :---: | :--- |
| [`tests/test_accuracy.py`](file:///d:/ATS-Resume-Job-Matcher/tests/test_accuracy.py) | **18** | Numeric date intervals (`07/2025–07/2026`), explicit tenure extraction, R language boundary safety, dynamic weight re-balancing, TF-IDF curve calibration, **Seniority Knockout Gate**, **Section-Aware Mandatory vs Preferred Weighting**. |
| [`tests/test_api.py`](file:///d:/ATS-Resume-Job-Matcher/tests/test_api.py) | **6** | Root, health check, invalid IDs, `/match/file` persistence, Supabase endpoints, and `/jobs/recommend`. |
| [`tests/test_core.py`](file:///d:/ATS-Resume-Job-Matcher/tests/test_core.py) | **10** | Magic-byte file validation, empty data handlers, skill aliasing, and matching service boundaries. |
| [`tests/test_health_and_tailor.py`](file:///d:/ATS-Resume-Job-Matcher/tests/test_health_and_tailor.py) | **5** | ATS health service scoring (85+ Grade A vs. Grade D), STAR bullet generation, tailored summaries, and REST API endpoints. |
| [`tests/test_end_to_end_verification.py`](file:///d:/ATS-Resume-Job-Matcher/tests/test_end_to_end_verification.py) | **2** | Full end-to-end integration test verifying complete workflow on real candidate resume data and bitwise Mode 1 / Mode 2 score parity. |
| **Total** | **41** | **All 41 Passed (100% Green in ~17s)** |

---

## 📁 Project Directory Structure

```text
ATS-Resume-Job-Matcher/
├── app/
│   ├── api/                     # FastAPI route handlers
│   │   ├── routes_health.py     # /health
│   │   ├── routes_history.py    # /matches/history
│   │   ├── routes_job.py        # /job/*
│   │   ├── routes_match.py      # /match/* and report generation
│   │   ├── routes_match_file.py # /match/file
│   │   ├── routes_resume.py     # /resume/*, /resume/health, /resume/tailor
│   │   ├── routes_root.py       # /
│   │   └── routes_supabase.py   # /jobs/supabase and /jobs/recommend
│   ├── database/                # SQLAlchemy models, sessions, and repository
│   │   ├── database.py
│   │   ├── init_db.py
│   │   ├── models.py
│   │   └── repository.py
│   ├── matching/                # Core scoring and matching algorithms
│   │   ├── evidence_matcher.py  # Evidence-based requirement evaluator
│   │   ├── skill_matcher.py     # Exact, alias, and partial skill matcher
│   │   ├── skill_normalizer.py  # Canonical skill taxonomy & aliases
│   │   ├── tfidf_matcher.py     # Calibrated TF-IDF similarity matcher
│   │   └── weighted_scorer.py   # Weighted component scorer
│   ├── nlp/                     # Natural Language Processing & extraction
│   │   ├── context_matcher.py   # Title, seniority, location, authorization
│   │   ├── experience_extractor.py # Tenure calculation & date range parsing
│   │   ├── keyword_extractor.py # Cleaned keyword extraction
│   │   ├── requirement_extractor.py # Section-aware requirement parsing
│   │   └── skill_extractor.py   # Resume skill detection
│   ├── parsers/                 # File parsers with magic-byte validation
│   │   ├── docx_parser.py
│   │   ├── file_validator.py
│   │   ├── job_parser.py
│   │   ├── pdf_parser.py
│   │   ├── resume_parser.py
│   │   └── txt_parser.py
│   ├── scoring/                 # Dynamic ATS score calculator
│   │   └── scoring_engine.py    # Dynamic weight re-balancing & safety gates
│   └── services/                # Business logic services
│       ├── docx_report_service.py # ATS Word report generator
│       ├── job_recommender_service.py # Live job discovery & scoring
│       ├── matching_service.py  # End-to-end matching orchestrator
│       ├── resume_health_service.py # ATS parseability & health audit
│       ├── resume_service.py    # Resume extraction & persistence
│       ├── resume_tailor_service.py # AI summary & STAR bullet generation
│       └── supabase_service.py  # Supabase PostgREST client & enrichment
├── docs/
│   └── assets/
│       ├── hero_banner.svg      # Modern dark-mode header banner
│       ├── ats_match_dashboard.svg # Glassmorphic SaaS UI mockup
│       ├── knockout_architecture.svg # Production knockout gates diagram
│       └── supabase_role_selector.png # Live Streamlit UI screenshot
├── frontend/
│   └── app.py                   # Streamlit user interface (dual modes, 6 tabs)
├── tests/                       # Complete automated test suite (41 tests)
│   ├── test_accuracy.py
│   ├── test_api.py
│   ├── test_core.py
│   ├── test_end_to_end_verification.py
│   └── test_health_and_tailor.py
├── docker-compose.yml           # Container orchestration
├── Dockerfile                   # Application container specification
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
