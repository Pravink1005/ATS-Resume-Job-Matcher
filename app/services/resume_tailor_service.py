import re
from typing import Dict, Any, List
from app.matching.skill_normalizer import normalize_skill
from app.nlp.skill_extractor import extract_skills


class ResumeTailorService:
    """Generates tailored resume summaries, STAR-format bullet points, and ATS optimization advice."""

    # STAR-method templates crafted with strong action verbs, context, and quantifiable results
    STAR_TEMPLATES = {
        # Backend & Cloud
        'docker': "Containerized backend microservices using Docker and multi-stage builds, reducing deployment cycle times by 35% and standardizing developer environments across 4 distributed teams.",
        'kubernetes': "Orchestrated container deployments on Kubernetes (K8s) clusters with automated health probes and horizontal pod autoscaling, sustaining 99.9% service uptime during peak traffic.",
        'fastapi': "Architected high-throughput RESTful APIs with FastAPI and Pydantic, achieving sub-50ms average latency and supporting 10k+ concurrent requests.",
        'django': "Engineered scalable web applications and administrative dashboards using Django and PostgreSQL, streamlining internal business operations and cutting query latency by 40%.",
        'flask': "Developed lightweight microservices using Flask and Celery for asynchronous background job processing, handling 50k+ daily transactional tasks.",
        'spring boot': "Developed enterprise microservices with Spring Boot and Java, integrating secure JWT authentication and reducing system downtime by 25%.",
        'go': "Architected distributed backend services in Go (Golang) leveraging goroutines for concurrent processing, cutting server resource utilization by 30%.",
        'aws': "Designed and provisioned resilient cloud infrastructure on AWS utilizing EC2, S3, RDS, and Lambda, optimizing monthly cloud expenditure by 22%.",
        'azure': "Deployed enterprise applications to Microsoft Azure with App Services, Blob Storage, and Azure Functions, achieving 99.95% high availability.",
        'gcp': "Implemented cloud-native workflows on Google Cloud Platform (GCP) using BigQuery and Cloud Run, accelerating real-time data ingestion pipelines.",
        'ci/cd': "Built automated CI/CD pipelines with GitHub Actions and Jenkins, cutting production release cycles from 2 days to under 30 minutes with zero downtime.",
        'terraform': "Authored modular Infrastructure as Code (IaC) with Terraform, automating multi-environment provisioning and eliminating manual configuration drift.",
        'redis': "Implemented a Redis in-memory caching layer for frequently accessed query results, reducing database load by 60% and lowering p95 response times.",
        'microservices': "Refactored a monolithic backend architecture into modular microservices communicating via REST and gRPC, improving deployment independence and fault isolation.",

        # Additional High-Frequency Skills
        'api': "Designed, tested, and integrated resilient RESTful APIs, enabling seamless cross-service communication and achieving 99.9% request success rates.",
        'rest api': "Architected and documented production RESTful APIs with automated OpenAPI schemas, cutting partner integration onboarding times by 40%.",
        'linux': "Administered production Linux (Ubuntu/Debian) environments, automating server configuration, package management, and system monitoring with bash scripts.",
        'java': "Engineered enterprise backend microservices in Java, leveraging multithreading and clean design patterns to optimize application throughput.",
        'git': "Implemented Git version control workflows and branch management strategies, accelerating collaborative release pipelines and eliminating merge conflicts.",
        'jenkins': "Configured distributed Jenkins build nodes and automated declarative pipeline triggers, reducing build cycle times by 45%.",

        # Frontend & Web
        'react': "Developed responsive, accessible single-page web applications using React and modern hooks, enhancing mobile user engagement by 28% and user satisfaction scores.",
        'next.js': "Engineered server-side rendered (SSR) web applications with Next.js and TypeScript, reducing initial page load times by 45% and boosting SEO performance.",
        'typescript': "Migrated legacy JavaScript codebases to strict TypeScript, eliminating 75% of runtime type errors across critical user authentication and checkout flows.",
        'vue': "Built interactive, component-driven user interfaces using Vue.js and Pinia state management, delivering smooth 60fps UI animations.",
        'angular': "Maintained and enhanced large-scale single-page enterprise web applications utilizing Angular, RxJS, and TypeScript.",
        'tailwind': "Designed modern, responsive web layouts using Tailwind CSS, reducing CSS bundle sizes by 50% and accelerating UI component prototyping.",
        'node.js': "Built asynchronous backend event-driven services with Node.js and Express, scaling throughput to handle 5k+ API requests per minute.",

        # Data & AI / ML
        'python': "Engineered automated Python data processing scripts and ETL workflows, eliminating 15+ hours of manual data extraction and validation each week.",
        'sql': "Constructed and optimized complex SQL queries with CTEs and indexing across multi-million-row databases, accelerating executive reporting queries by 50%.",
        'postgresql': "Managed and tuned relational PostgreSQL databases, optimizing schema indexes and connection pools to support high-throughput read/write operations.",
        'mongodb': "Designed scalable NoSQL document data models in MongoDB, supporting flexible data schemas for high-velocity IoT and telemetry event logs.",
        'pandas': "Spearheaded exploratory data analysis and data cleansing workflows with Pandas, processing 2M+ records to uncover key trends and business drivers.",
        'power bi': "Created executive Power BI dashboards with real-time KPI tracking and automated daily data refreshes, empowering leadership with actionable business insights.",
        'tableau': "Designed comprehensive Tableau visualizations and interactive dashboards, presenting cross-departmental sales and marketing trends to C-level stakeholders.",
        'etl': "Engineered end-to-end automated ETL data pipelines extracting data from 6 distinct APIs, validating data integrity and loading into a centralized warehouse.",
        'data cleaning': "Implemented robust data cleaning and anomaly detection pipelines, elevating dataset accuracy to 99.5% and reducing report discrepancies.",
        'machine learning': "Trained and deployed predictive machine learning models with Scikit-Learn, boosting churn prediction accuracy by 18% over baseline benchmarks.",
        'pytorch': "Built and fine-tuned deep learning neural network models in PyTorch for computer vision and NLP classification tasks with 92% validation accuracy.",
        'llm': "Integrated Large Language Model (LLM) pipelines using LangChain and vector embeddings, automating document summarization and semantic customer search.",
        'airflow': "Orchestrated complex DAG workflows in Apache Airflow for scheduled batch data pipelines with automated retry alerts and SLA tracking.",
        'spark': "Processed terabyte-scale distributed datasets with Apache Spark (PySpark), reducing batch aggregation runtimes from 8 hours to 45 minutes.",
        'snowflake': "Engineered scalable cloud data warehousing architectures in Snowflake, optimizing compute warehouse sizing and cutting query expenses by 30%."
    }

    def __init__(self):
        pass

    def generate_tailored_recommendations(
        self,
        resume_text: str,
        job_description: str,
        match_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generates tailored professional summary, STAR bullet points, skills block, and placement strategy."""
        if not match_result:
            m_title = re.search(r'(?im)^\s*(?:job title|role|position)\s*:\s*(.+)$', job_description)
            target_title = m_title.group(1).strip() if m_title else (job_description.splitlines()[0].strip()[:150] if job_description.splitlines() else 'Target Role')
            res_skills = set(extract_skills(resume_text))
            jd_skills = set(extract_skills(job_description))
            matched_skills = sorted(res_skills.intersection(jd_skills))
            missing_skills = sorted(jd_skills - res_skills)
            exp_match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)', resume_text, re.I)
            exp_years = float(exp_match.group(1)) if exp_match else 0.0
            overall_score = 0.0
        else:
            target_title = match_result.get('job_title') or 'Target Role'
            missing_skills = match_result.get('missing_skills') or []
            matched_skills = match_result.get('matched_skills') or []
            exp_years = float(match_result.get('candidate_experience') or 0.0)
            overall_score = match_result.get('overall_score', 0.0)

        # 1. Generate Custom Tailored Professional Summary
        summary = self._generate_summary(target_title, exp_years, matched_skills, missing_skills, job_description)

        # 2. Generate STAR-Method Bullet Points (for missing skills, or showcasing matched strengths if none missing)
        tailored_bullets = self._generate_star_bullets(missing_skills, target_title, matched_skills)

        # 3. Categorized ATS Skills Section
        skills_section = self._format_skills_section(matched_skills, missing_skills)

        # 4. Actionable Keyword Placement Strategy
        placement_advice = self._generate_placement_strategy(target_title, missing_skills, match_result)

        return {
            'target_title': target_title,
            'overall_score': overall_score,
            'tailored_summary': summary,
            'star_bullet_points': tailored_bullets,
            'skills_section': skills_section,
            'placement_strategy': placement_advice,
            'missing_skills': missing_skills,
            'matched_skills': matched_skills,
        }

    def _generate_summary(
        self,
        target_title: str,
        exp_years: float,
        matched_skills: List[str],
        missing_skills: List[str],
        job_desc: str
    ) -> str:
        top_skills = [s.title() for s in matched_skills[:4]]
        skills_str = ', '.join(top_skills) if top_skills else 'software development and problem-solving'

        exp_clause = f"with {exp_years:g}+ years of experience" if exp_years > 0 else "with a strong background"

        # Sentence 1: Role identity & proven technical foundation
        s1 = f"Results-driven {target_title} {exp_clause} specializing in {skills_str}."

        # Sentence 2: Execution & business value
        if any(w in job_desc.lower() for w in ['data', 'analytics', 'pipeline', 'bi']):
            s2 = "Demonstrated expertise in architecting resilient data pipelines, extracting actionable insights, and translating complex business requirements into high-impact solutions."
        elif any(w in job_desc.lower() for w in ['frontend', 'react', 'ui', 'web']):
            s2 = "Passionate about creating modern, responsive, and accessible user interfaces that deliver seamless customer experiences and superior performance."
        else:
            s2 = "Proven track record of designing, building, and scaling resilient systems that enhance operational efficiency and maintain high availability."

        # Sentence 3: Impact & alignment with target role
        target_tech = missing_skills[0].title() if missing_skills else "cutting-edge technologies"
        s3 = f"Eager to leverage core technical competencies in {skills_str} and continuous innovation with {target_tech} to drive measurable impact in the {target_title} role."

        return f"{s1} {s2} {s3}"

    def _generate_star_bullets(
        self,
        missing_skills: List[str],
        target_title: str,
        matched_skills: List[str] = None
    ) -> List[Dict[str, str]]:
        bullets = []

        if missing_skills:
            target_skills = missing_skills[:6]
            category_label = 'Missing High-Impact Skill'
        elif matched_skills:
            target_skills = matched_skills[:4]
            category_label = 'Core Matched Strength'
        else:
            target_skills = []
            category_label = 'General Technical Competency'

        for raw_skill in target_skills:
            canon = normalize_skill(raw_skill)
            display_skill = raw_skill.title()

            # Find matching template or generate dynamic STAR bullet
            if canon in self.STAR_TEMPLATES:
                bullet_text = self.STAR_TEMPLATES[canon]
            else:
                bullet_text = (
                    f"Implemented scalable {display_skill} solutions within development workflows, "
                    f"streamlining cross-functional operations and enhancing team delivery efficiency by 25%."
                )

            bullets.append({
                'skill': display_skill,
                'category': category_label,
                'bullet_point': bullet_text,
                'formula': 'Action Verb + Skill Context + Measurable Impact (STAR method)'
            })

        return bullets

    def _format_skills_section(self, matched_skills: List[str], missing_skills: List[str]) -> Dict[str, Any]:
        all_matched = sorted([s.title() for s in matched_skills])
        top_missing = sorted([s.title() for s in missing_skills[:6]])

        copy_paste_text = (
            f"Core Technologies: {', '.join(all_matched)}\n"
            f"Recommended Additions: {', '.join(top_missing)}"
        )

        return {
            'matched_skills': all_matched,
            'recommended_additions': top_missing,
            'formatted_copy_paste': copy_paste_text
        }

    def _generate_placement_strategy(
        self,
        target_title: str,
        missing_skills: List[str],
        match_result: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        steps = [
            {
                'section': 'Target Job Title & Header',
                'action': f'Align your resume header or professional title to "{target_title}".',
                'reason': 'ATS parsing engines match exact title strings in the first 200 characters for immediate relevance weighting.'
            },
            {
                'section': 'Professional Summary',
                'action': 'Use the tailored 3-sentence summary generated above right beneath your contact details.',
                'reason': 'Recruiters spend an average of 6 seconds scanning the summary for required keywords before reading bullet points.'
            }
        ]

        if missing_skills:
            top_miss = [s.title() for s in missing_skills[:3]]
            steps.append({
                'section': 'Work Experience (STAR Bullets)',
                'action': f'Incorporate STAR bullet points for {", ".join(top_miss)} into your most recent work experience or project section.',
                'reason': 'Evidence-based ATS algorithms give 3x more weight to keywords embedded in experience bullets than standalone lists.'
            })
            steps.append({
                'section': 'Skills List',
                'action': f'Add {", ".join(top_miss)} into your technical skills block under relevant subheadings.',
                'reason': 'Ensures deterministic keyword extractors capture the exact skill strings without ambiguity.'
            })

        return steps
