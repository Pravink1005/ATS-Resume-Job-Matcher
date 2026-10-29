import csv
from io import BytesIO, StringIO
import os

import altair as alt
import pandas as pd
import requests
import streamlit as st
from docx import Document


API_URL = os.getenv('MATCHER_API_URL', 'http://127.0.0.1:8000').rstrip('/')

st.set_page_config(
    page_title='ResumeMatch ATS | Next-Gen AI Career & Match Intelligence',
    page_icon='⚡',
    layout='wide',
    initial_sidebar_state='collapsed',
)

# ==============================================================================
# BESPOKE MODERN DESIGN SYSTEM (GLASSMORPHISM + NEON ACCENTS + POLISHED CARDS)
# ==============================================================================
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    max-width: 1240px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

/* Hero Header */
.hero-wrapper {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(99, 102, 241, 0.28);
    border-radius: 20px;
    padding: 2.2rem 2.6rem;
    margin-bottom: 1.6rem;
    box-shadow: 0 16px 40px -12px rgba(0, 0, 0, 0.5), 0 0 35px -10px rgba(99, 102, 241, 0.22);
    position: relative;
    overflow: hidden;
}

.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -15%;
    width: 420px;
    height: 420px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.28) 0%, rgba(168, 85, 247, 0.12) 50%, transparent 70%);
    filter: blur(45px);
    pointer-events: none;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: rgba(99, 102, 241, 0.16);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.35);
    margin-bottom: 0.8rem;
}

.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 0.5rem 0;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 45%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.08rem;
    color: #94a3b8;
    margin: 0 0 1.2rem 0;
    max-width: 820px;
    line-height: 1.5;
}

.status-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 0.82rem;
    color: #94a3b8;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.04);
    padding: 5px 13px;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.09);
    color: #cbd5e1;
    font-weight: 500;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Skill Pills */
.skill-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin: 3px 4px 3px 0;
    transition: transform 0.15s ease;
}
.skill-pill:hover {
    transform: translateY(-1px);
}
.pill-match {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
}
.pill-alias {
    background: rgba(14, 165, 233, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.35);
}
.pill-missing {
    background: rgba(244, 63, 94, 0.15);
    color: #fb7185;
    border: 1px solid rgba(244, 63, 94, 0.35);
}
.pill-preferred {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.35);
}
.pill-neutral {
    background: rgba(148, 163, 184, 0.12);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.25);
}

/* Metric / Stat Card */
.stat-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.stat-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(99, 102, 241, 0.06);
    transform: translateY(-1px);
}
.stat-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.stat-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #f8fafc;
}
.stat-sub {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 0.2rem;
}

/* Modern Card Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.3) !important;
}

/* File Uploader override */
div[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1.5px dashed rgba(99, 102, 241, 0.4);
    border-radius: 14px;
    padding: 0.9rem;
    transition: border-color 0.2s ease;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(129, 140, 248, 0.8);
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(79, 70, 229, 0.4) !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 6px 24px rgba(79, 70, 229, 0.6) !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
button[kind="secondary"]:hover {
    border-color: rgba(99, 102, 241, 0.5) !important;
    background: rgba(99, 102, 241, 0.1) !important;
    transform: translateY(-1px) !important;
}

/* Job Recommender Card */
.job-card-wrapper {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 6px 20px -8px rgba(0, 0, 0, 0.35);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.job-card-wrapper:hover {
    border-color: rgba(99, 102, 241, 0.45);
    box-shadow: 0 12px 32px -10px rgba(99, 102, 241, 0.25);
    transform: translateY(-2px);
}
</style>''', unsafe_allow_html=True)


# ==============================================================================
# UI HELPER FUNCTIONS & VISUAL COMPONENTS
# ==============================================================================
def api_error(response):
    try:
        detail = response.json().get('detail')
        if isinstance(detail, str) and detail:
            return detail
    except (ValueError, requests.RequestException):
        pass
    return f'Backend returned status {response.status_code}.'


def render_skill_pills(skills, pill_type="match"):
    if not skills:
        return '<span class="skill-pill pill-neutral">None identified</span>'
    icons = {"match": "✓", "alias": "≈", "missing": "✕", "preferred": "★", "neutral": "•"}
    icon = icons.get(pill_type, "•")
    html = []
    for s in skills:
        html.append(f'<span class="skill-pill pill-{pill_type}">{icon} {s}</span>')
    return "".join(html)


def status_label(status):
    return status or 'Not available'


def render_svg_gauge(score: float, recommendation: str, size: int = 200) -> str:
    radius = 70
    circumference = 2 * 3.14159 * radius
    stroke_dashoffset = circumference - (min(100.0, max(0.0, score)) / 100.0) * circumference

    if score >= 75:
        stroke_color = "#10b981"
        glow_color = "rgba(16, 185, 129, 0.4)"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        badge_border = "rgba(16, 185, 129, 0.35)"
        badge_text = "#34d399"
        tier_label = "EXCELLENT MATCH"
    elif score >= 55:
        stroke_color = "#0ea5e9"
        glow_color = "rgba(14, 165, 233, 0.4)"
        badge_bg = "rgba(14, 165, 233, 0.15)"
        badge_border = "rgba(14, 165, 233, 0.35)"
        badge_text = "#38bdf8"
        tier_label = "STRONG FIT"
    elif score >= 40:
        stroke_color = "#f59e0b"
        glow_color = "rgba(245, 158, 11, 0.4)"
        badge_bg = "rgba(245, 158, 11, 0.15)"
        badge_border = "rgba(245, 158, 11, 0.35)"
        badge_text = "#fbbf24"
        tier_label = "MODERATE FIT"
    else:
        stroke_color = "#f43f5e"
        glow_color = "rgba(244, 63, 94, 0.4)"
        badge_bg = "rgba(244, 63, 94, 0.15)"
        badge_border = "rgba(244, 63, 94, 0.35)"
        badge_text = "#fb7185"
        tier_label = "NEEDS REVISION"

    return f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1.6rem 1rem;background:radial-gradient(circle, {glow_color.replace('0.4','0.08')} 0%, rgba(15,23,42,0.6) 100%);border:1px solid {badge_border};border-radius:20px;box-shadow:0 12px 30px -8px rgba(0,0,0,0.5);">
        <svg width="{size}" height="{size}" viewBox="0 0 180 180">
            <circle cx="90" cy="90" r="{radius}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12" />
            <circle cx="90" cy="90" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="12"
                stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}"
                stroke-linecap="round" transform="rotate(-90 90 90)"
                style="filter: drop-shadow(0 0 8px {stroke_color});" />
            <text x="90" y="86" text-anchor="middle" fill="#ffffff" font-size="34" font-weight="800" font-family="'Plus Jakarta Sans', sans-serif">{score:.1f}%</text>
            <text x="90" y="108" text-anchor="middle" fill="#94a3b8" font-size="11" font-weight="600" letter-spacing="1.5" font-family="'Plus Jakarta Sans', sans-serif">ATS SCORE</text>
        </svg>
        <div style="margin-top:0.8rem;padding:5px 16px;border-radius:9999px;background:{badge_bg};border:1px solid {badge_border};color:{badge_text};font-size:0.8rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;">
            {tier_label}
        </div>
        <div style="margin-top:0.6rem;font-size:0.95rem;color:#f1f5f9;font-weight:600;text-align:center;">
            {recommendation}
        </div>
    </div>
    """


def render_grade_circle(grade: str, score: int) -> str:
    color_map = {
        'A': ('#10b981', 'rgba(16, 185, 129, 0.25)', '#34d399'),
        'B': ('#0ea5e9', 'rgba(14, 165, 233, 0.25)', '#38bdf8'),
        'C': ('#f59e0b', 'rgba(245, 158, 11, 0.25)', '#fbbf24'),
        'D': ('#f43f5e', 'rgba(244, 63, 94, 0.25)', '#fb7185'),
    }
    c_main, c_bg, c_border = color_map.get(grade.upper(), ('#818cf8', 'rgba(129, 140, 248, 0.25)', '#a5b4fc'))

    return f"""
    <div style="display:flex;align-items:center;gap:16px;padding:1.2rem;background:{c_bg};border:1px solid {c_border};border-radius:18px;">
        <div style="display:flex;align-items:center;justify-content:center;width:68px;height:68px;border-radius:50%;background:{c_main};color:#ffffff;font-size:2rem;font-weight:800;box-shadow:0 0 18px {c_main};">
            {grade}
        </div>
        <div>
            <div style="font-size:1.35rem;font-weight:800;color:#f8fafc;">{score}/100</div>
            <div style="font-size:0.82rem;font-weight:600;color:{c_border};text-transform:uppercase;letter-spacing:0.05em;">ATS Parseability Health</div>
        </div>
    </div>
    """


def build_score_breakdown_chart(scores_dict: dict):
    categories = [
        ('Technical Skills', 'skills', 35),
        ('Experience Fit', 'experience', 25),
        ('Competencies', 'competencies', 15),
        ('Semantic Similarity', 'tfidf', 15),
        ('Education', 'education', 10),
    ]
    data = []
    for label, key, weight in categories:
        val = float(scores_dict.get(key, 0))
        data.append({
            'Category': label,
            'Score': val,
            'Weight': f'{weight}% weight',
            'ScoreText': f'{val:.1f}%'
        })
    df = pd.DataFrame(data)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadius=6, height=18)
        .encode(
            x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100]), title='Score (%)'),
            y=alt.Y('Category:N', sort=None, title=None),
            color=alt.Color(
                'Score:Q',
                scale=alt.Scale(scheme='tealblues', domain=[0, 100]),
                legend=None,
            ),
            tooltip=['Category', 'ScoreText', 'Weight'],
        )
        .properties(height=200)
    )
    return chart


def build_docx_report(data, resume_name):
    document = Document()
    document.add_heading('ResumeMatch ATS Report', level=0)
    document.add_paragraph(f'Resume: {resume_name}')
    document.add_heading('Match Summary', level=1)
    document.add_paragraph(
        f'Overall score: {float(data.get("overall_score", 0)):.1f}%\n'
        f'Recommendation: {data.get("recommendation", "Not available")}'
    )

    document.add_heading('Score Breakdown', level=1)
    scores = data.get('component_scores', {})
    table = document.add_table(rows=1, cols=2)
    table.style = 'Light Shading Accent 1'
    table.rows[0].cells[0].text = 'Category'
    table.rows[0].cells[1].text = 'Score'
    for label, key in [
        ('Skills', 'skills'), ('Experience', 'experience'), ('Education', 'education'),
        ('Competencies', 'competencies'), ('Keywords', 'keywords'), ('Similarity', 'tfidf'),
    ]:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = f'{float(scores.get(key, 0)):.1f}%'

    document.add_heading('Skills', level=1)
    document.add_paragraph('Matched: ' + ', '.join(data.get('matched_skills', []) or ['None identified']))
    document.add_paragraph('To improve: ' + ', '.join(data.get('missing_skills', []) or ['None identified']))
    document.add_heading('Experience and Education', level=1)
    document.add_paragraph(
        f'Candidate experience: {float(data.get("candidate_experience", 0)):g} years\n'
        f'Required experience: {float(data.get("required_experience", 0)):g} years\n'
        f'Experience gap: {float(data.get("experience_gap", 0)):g} years\n'
        f'Experience status: {status_label(data.get("experience_status"))}\n'
        f'Education: {status_label(data.get("education_status"))}'
    )

    document.add_heading('Requirement Evidence', level=1)
    requirements = data.get('requirement_analysis', [])
    if requirements:
        for requirement in requirements:
            document.add_paragraph(
                f'{requirement.get("name", requirement.get("canonical", "Requirement"))}: '
                f'{requirement.get("status", "unknown").title()} '
                f'({float(requirement.get("score", 0)):.0f}%)\n'
                f'Evidence: {requirement.get("evidence", "No evidence provided.")}',
                style='List Bullet',
            )
    else:
        document.add_paragraph('Requirement-level evidence was not included in the API response.')

    document.add_heading('ATS Notes', level=1)
    for explanation in data.get('explanations', []):
        document.add_paragraph(explanation, style='List Bullet')

    health = data.get('resume_health')
    if health:
        document.add_heading('ATS Resume Health & Parseability', level=1)
        document.add_paragraph(
            f"Health score: {health.get('health_score', 0)}/100 (Grade: {health.get('grade', 'N/A')})\n"
            f"Word count: {health.get('word_count', 0)} words (~{health.get('page_estimate', 1)} page(s))\n"
            f"Quantifiable metrics detected: {len(health.get('metrics_found', []))}\n"
            f"Action verbs detected: {len(health.get('action_verbs_found', []))}"
        )

    tailoring = data.get('tailoring_suggestions')
    if tailoring:
        document.add_heading('Tailored Professional Summary', level=1)
        document.add_paragraph(tailoring.get('tailored_summary', ''))

        document.add_heading('STAR Method Bullet Points (Tailored for Missing Skills)', level=1)
        for bullet in tailoring.get('star_bullet_points', []):
            document.add_paragraph(
                f"[{bullet.get('skill', '')}] {bullet.get('bullet_point', '')}",
                style='List Bullet'
            )

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def build_recommendations_csv(recommendations: list) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Rank',
        'Job Title',
        'Company',
        'Location',
        'ATS Match Score',
        'Recommendation Fit',
        'Matched Skills',
        'Missing Skills',
        'Candidate Experience (Years)',
        'Required Experience (Years)',
        'Experience Status',
        'Time Posted',
        'Application URL',
        'Application Status',
        'Notes'
    ])
    for idx, r in enumerate(recommendations, start=1):
        matched_str = ', '.join(r.get('matched_skills', []))
        missing_str = ', '.join(r.get('missing_skills', []))
        writer.writerow([
            idx,
            r.get('title', 'Unknown Title'),
            r.get('company', 'Unknown Company'),
            r.get('location', 'Location Not Specified'),
            f"{float(r.get('overall_score', 0)):.1f}%",
            r.get('recommendation', 'Not Available'),
            matched_str,
            missing_str,
            f"{float(r.get('candidate_experience', 0)):.1f}",
            f"{float(r.get('required_experience', 0)):.1f}",
            r.get('experience_status', ''),
            r.get('posted_label', 'Recent'),
            r.get('link', ''),
            'To Apply',
            ''
        ])
    return output.getvalue()


# Handle 1-Click Deep Match routing from Mode 2
if st.session_state.get('pending_inspect_job'):
    target_job = st.session_state.pop('pending_inspect_job')
    st.session_state['result'] = target_job
    st.session_state['active_chosen_job_id'] = target_job.get('job_id')
    st.session_state['jd_supabase_text'] = target_job.get('description', '')
    st.session_state['main_nav_mode'] = '🎯 Mode 1: Deep Single Job Match'
    if not st.session_state.get('resume_name') and st.session_state.get('saved_resume_tuple'):
        st.session_state['resume_name'] = st.session_state['saved_resume_tuple'][0]

# Handle pending navigation mode switch (e.g. Back to Top Search Recommendations)
if st.session_state.get('pending_nav_mode'):
    st.session_state['main_nav_mode'] = st.session_state.pop('pending_nav_mode')


# ==============================================================================
# HERO HEADER & BRAND STATUS BAR
# ==============================================================================
st.markdown('''
<div class="hero-wrapper">
    <div class="badge-tag">⚡ Next-Gen ATS Intelligence Platform</div>
    <h1 class="hero-title">ResumeMatch ATS</h1>
    <p class="hero-subtitle">
        Explainable resume matching, dynamic weight re-balancing, real-time career discovery across 6,200+ roles, 
        and AI-powered resume tailoring with STAR-formula optimization.
    </p>
    <div class="status-bar">
        <div class="status-item"><span class="pulse-dot"></span> Supabase Cloud Connected (6,200+ Live Jobs)</div>
        <div class="status-item">⚡ Calibrated TF-IDF Engine Active</div>
        <div class="status-item">⚖️ Dynamic Re-balancing Active</div>
        <div class="status-item">🎯 STAR Resume Tailor Ready</div>
    </div>
</div>
''', unsafe_allow_html=True)

main_nav = st.radio(
    'Select Workflow Mode:',
    ['🎯 Mode 1: Deep Single Job Match', '🚀 Mode 2: Auto-Job Recommender (6,200+ Live Jobs)'],
    horizontal=True,
    key='main_nav_mode'
)

st.write('')


# ==============================================================================
# MODE 1: DEEP SINGLE JOB MATCH
# ==============================================================================
if main_nav == '🎯 Mode 1: Deep Single Job Match':
    if st.session_state.get('recommendations_data'):
        back_col1, back_col2 = st.columns([1.8, 3])
        with back_col1:
            if st.button('⬅️ Back to Top Search Recommendations', key='btn_back_to_recs_banner', type='secondary', use_container_width=True):
                st.session_state['pending_nav_mode'] = '🚀 Mode 2: Auto-Job Recommender (6,200+ Live Jobs)'
                st.rerun()
        with back_col2:
            num_recs = len(st.session_state['recommendations_data'].get('recommendations', []))
            st.caption(f'💡 Deep inspecting selected role. Return to your {num_recs} ranked job recommendations anytime.')
        st.write('')

    with st.container(border=True):
        st.markdown('### 🎯 Configure Single Job Evaluation')
        input_col, job_col = st.columns(2, gap='large')

        with input_col:
            st.markdown('**1. Upload Candidate Resume**')
            resume = st.file_uploader(
                'Resume File (PDF, DOCX, TXT):',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False,
                key='single_resume_uploader',
                help='Supported formats: PDF, DOCX, and TXT with magic-byte header validation.',
            )
            if resume:
                st.session_state['saved_resume_tuple'] = (resume.name, resume.getvalue(), resume.type)
                st.markdown(
                    f'<div style="padding:6px 12px;border-radius:8px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:#34d399;font-size:0.85rem;font-weight:600;">'
                    f'✓ {resume.name} loaded ({resume.size / 1024:.0f} KB)</div>',
                    unsafe_allow_html=True
                )
            elif st.session_state.get('saved_resume_tuple'):
                saved_name = st.session_state['saved_resume_tuple'][0]
                st.markdown(
                    f'<div style="padding:6px 12px;border-radius:8px;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;font-size:0.85rem;font-weight:600;">'
                    f'ℹ️ Using active resume: {saved_name}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.caption('Upload a resume file to extract skills, tenure, and health score.')

        with job_col:
            st.markdown('**2. Target Job Criteria**')
            source_mode = st.radio(
                'Job Source Selection:',
                ['🗄️ Supabase Role Database', '📋 Paste Description'],
                horizontal=True,
                help='Choose whether to pick from the live Supabase database or manually paste raw job text.'
            )

            if source_mode == '🗄️ Supabase Role Database':
                search_col1, search_col2 = st.columns([2, 1])
                with search_col1:
                    search_q = st.text_input(
                        'Search role / keyword / company:',
                        placeholder='e.g. Data Analyst, Software Engineer, Python',
                        key='sb_search_q'
                    )
                with search_col2:
                    cat_options = ['All']
                    try:
                        kw_res = requests.get(f'{API_URL}/supabase/keywords', timeout=4)
                        if kw_res.ok:
                            cat_options.extend(kw_res.json().get('keywords', []))
                    except Exception:
                        pass
                    selected_cat = st.selectbox('Category:', options=cat_options, key='sb_cat')

                fetched_jobs = []
                try:
                    cat_filter = '' if selected_cat == 'All' else selected_cat
                    jobs_res = requests.get(
                        f'{API_URL}/supabase/jobs',
                        params={'query': search_q, 'keyword': cat_filter, 'limit': 40},
                        timeout=6
                    )
                    if jobs_res.ok:
                        fetched_jobs = jobs_res.json().get('jobs', [])
                except Exception:
                    pass

                if fetched_jobs:
                    job_map = {j['label']: j for j in fetched_jobs}
                    labels = list(job_map.keys())

                    selected_job_label = st.selectbox(
                        f'Select Target Role ({len(fetched_jobs)} matching roles):',
                        options=labels,
                        key='sb_selected_job'
                    )
                    chosen_job = job_map[selected_job_label]

                    # Auto-update description whenever selected role changes
                    if st.session_state.get('active_chosen_job_id') != chosen_job['job_id']:
                        st.session_state['active_chosen_job_id'] = chosen_job['job_id']
                        st.session_state['jd_supabase_text'] = chosen_job['description']

                    jd = st.text_area(
                        'Selected Job Description (editable):',
                        key='jd_supabase_text',
                        height=160,
                        help='Loaded live from Supabase. You can edit text before running match analysis.',
                    )
                    desc_badge = "🟢 Full JD" if chosen_job.get('has_full_description') else "📋 Enriched Brief Summary"
                    st.caption(
                        f"🏢 **{chosen_job['company']}** | 📍 **{chosen_job['location']}** | 📝 {len(jd.split()):,} words | {desc_badge}"
                    )
                    if chosen_job.get('link'):
                        st.markdown(f"[🔗 View / Apply on LinkedIn]({chosen_job['link']})")
                else:
                    st.info('No matching jobs found in Supabase. Try adjusting your search term or category.')
                    jd = ''
            else:
                jd = st.text_area(
                    'Paste complete job description:',
                    height=200,
                    placeholder='Paste job requirements, responsibilities, skills, and qualifications here...',
                    help='Include technical skills, minimum experience, and education for the most thorough ATS evaluation.',
                    key='jd_paste_text'
                )
                if jd.strip():
                    st.caption(f'📝 {len(jd.split()):,} words')
                else:
                    st.caption('Paste a job description to proceed.')

        action_col, clear_col, status_col = st.columns([2, 1, 2])
        with action_col:
            analyze = st.button('🚀 Analyze Resume & Match', type='primary', use_container_width=True)
        with clear_col:
            clear = st.button('🗑️ Clear Results', use_container_width=True, disabled='result' not in st.session_state)
        with status_col:
            try:
                health = requests.get(f'{API_URL}/health', timeout=3)
                if health.ok:
                    st.markdown(
                        '<div style="display:flex;align-items:center;gap:6px;padding:8px 12px;border-radius:10px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:#34d399;font-size:0.85rem;font-weight:600;">'
                        '<span class="pulse-dot"></span> Backend API Connected & Ready</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning('⚠️ Backend API requires attention')
            except requests.RequestException:
                st.warning('⚠️ Backend API Offline')

        with st.expander('📜 View Previous Match History', expanded=False):
            try:
                matches_res = requests.get(f'{API_URL}/matches', timeout=3)
                if matches_res.ok and matches_res.json():
                    past_matches = matches_res.json()
                    st.caption(f'Found {len(past_matches)} recorded evaluation(s) in local SQLite database.')
                    match_options = {
                        f"#{m['match_id']} | {m['job_title']} ({m['resume_name']}) - {m['overall_score']:.1f}% [{m['recommendation']}] - {m['created_at']}": m['match_id']
                        for m in past_matches
                    }
                    selected_label = st.selectbox('Select past match record:', options=list(match_options.keys()))
                    if st.button('Load Evaluation Details', use_container_width=False):
                        sel_id = match_options[selected_label]
                        detail_res = requests.get(f'{API_URL}/match/{sel_id}', timeout=5)
                        if detail_res.ok:
                            st.session_state['result'] = detail_res.json()
                            st.session_state['resume_name'] = next((m['resume_name'] for m in past_matches if m['match_id'] == sel_id), 'resume')
                            st.success(f"Evaluation #{sel_id} loaded successfully!")
                            st.rerun()
                        else:
                            st.error('Could not retrieve evaluation details from backend.')
                else:
                    st.info('No previous evaluations recorded in local database.')
            except Exception:
                st.caption('Unable to load match history (backend offline).')

    if clear:
        st.session_state.pop('result', None)
        st.session_state.pop('resume_name', None)
        st.rerun()

    if analyze:
        if not resume and not st.session_state.get('saved_resume_tuple'):
            st.warning('⚠️ Please upload a resume file (PDF, DOCX, or TXT) in the left panel first.')
        elif not jd or not jd.strip():
            st.warning('⚠️ Please select a role from Supabase or paste a job description on the right first.')
        else:
            upload_tuple = (resume.name, resume.getvalue(), resume.type) if resume else st.session_state.get('saved_resume_tuple')
            try:
                with st.spinner('Parsing resume, verifying evidence, and running dynamic scoring engine...'):
                    response = requests.post(
                        f'{API_URL}/match/file',
                        files={'resume_file': upload_tuple},
                        data={'job_description': jd},
                        timeout=90,
                    )
                if not response.ok:
                    st.error(api_error(response))
                else:
                    st.session_state['result'] = response.json()
                    st.session_state['resume_name'] = upload_tuple[0]
                    st.success('ATS Evaluation Complete!')
                    st.rerun()
            except requests.RequestException:
                st.error(f'Could not connect to the matching API at {API_URL}. Start Uvicorn and try again.')
            except ValueError:
                st.error('Backend returned an invalid response. Check backend logs.')

    # ==============================================================================
    # RESULTS DASHBOARD
    # ==============================================================================
    if 'result' in st.session_state:
        data = st.session_state['result']
        scores = data.get('component_scores', {})
        overall = float(data.get('overall_score', 0))

        st.write('')
        st.markdown('---')

        # Executive Match Header Card
        score_col, summary_col = st.columns([1, 2], gap='large')
        with score_col:
            st.markdown(render_svg_gauge(overall, data.get('recommendation', 'Fit Result'), size=190), unsafe_allow_html=True)

        with summary_col:
            st.markdown(f"## {data.get('recommendation', 'Match Analysis Result')}")
            res_label = st.session_state.get("resume_name", "Resume")
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:0.8rem;">'
                f'<span class="skill-pill pill-neutral">📄 File: {res_label}</span>'
                f'<span class="skill-pill pill-match">✓ {len(data.get("matched_skills", []))} Matched Skills</span>'
                f'<span class="skill-pill pill-missing">✕ {len(data.get("missing_skills", []))} Skill Gaps</span>'
                f'<span class="skill-pill pill-alias">⏱️ {float(data.get("candidate_experience", 0)):.1f} yrs Candidate Tenure</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.write(
                'Objective evaluation synthesized from direct textual evidence, structured experience tenure calculation, '
                'education relevance, soft competencies, and calibrated TF-IDF semantic corpus similarity.'
            )

            action_btn_col1, action_btn_col2 = st.columns([1.2, 1.2])
            with action_btn_col1:
                st.download_button(
                    '📥 Download Formatted DOCX Report',
                    data=build_docx_report(data, st.session_state.get('resume_name', 'resume')),
                    file_name='ResumeMatch_ATS_Report.docx',
                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    use_container_width=True,
                )
            with action_btn_col2:
                if st.session_state.get('recommendations_data'):
                    if st.button('⬅️ Back to Top Search Recommendations', key='btn_back_to_recs_results', type='secondary', use_container_width=True):
                        st.session_state['pending_nav_mode'] = '🚀 Mode 2: Auto-Job Recommender (6,200+ Live Jobs)'
                        st.rerun()

        st.write('')

        # 6 Interactive Analysis Tabs
        tabs = st.tabs([
            '📊 Score Breakdown & Overview',
            '🎯 AI Resume Tailor',
            '🩺 ATS Health Check',
            '📋 Requirement Evidence',
            '🔍 Semantic & Competencies',
            '💡 ATS Insights & Notes'
        ])

        # TAB 1: OVERVIEW & BREAKDOWN
        with tabs[0]:
            st.markdown('### 📊 Category Score Breakdown')
            chart_col, stat_col = st.columns([1.6, 1], gap='large')
            with chart_col:
                st.altair_chart(build_score_breakdown_chart(scores), use_container_width=True)
            with stat_col:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-title">Technical Skills</div>'
                        f'<div class="stat-value">{float(scores.get("skills", 0)):.1f}%</div>'
                        f'<div class="stat-sub">35% base weight</div></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-title">Experience Fit</div>'
                        f'<div class="stat-value">{float(scores.get("experience", 0)):.1f}%</div>'
                        f'<div class="stat-sub">25% base weight</div></div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-title">Semantic Sim</div>'
                        f'<div class="stat-value">{float(scores.get("tfidf", 0)):.1f}%</div>'
                        f'<div class="stat-sub">15% base weight</div></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div class="stat-card"><div class="stat-title">Competencies</div>'
                        f'<div class="stat-value">{float(scores.get("competencies", 0)):.1f}%</div>'
                        f'<div class="stat-sub">15% base weight</div></div>',
                        unsafe_allow_html=True
                    )

            st.write('')
            left_col, right_col = st.columns(2, gap='large')
            with left_col:
                with st.container(border=True):
                    st.markdown('#### 🛠️ Technical Skills Evidence')
                    st.markdown('**Matched Skills:**')
                    st.markdown(render_skill_pills(data.get('matched_skills', []), 'match'), unsafe_allow_html=True)

                    st.markdown('**Skills to Improve / Missing:**')
                    st.markdown(render_skill_pills(data.get('missing_skills', []), 'missing'), unsafe_allow_html=True)

                    st.write('')
                    st.caption(
                        f"Exact: {len(data.get('exact_skill_matches', []))} | "
                        f"Canonical Alias: {len(data.get('alias_skill_matches', []))} | "
                        f"Partial: {len(data.get('partial_skill_matches', []))} | "
                        f"Related: {len(data.get('related_skill_matches', []))}"
                    )

            with right_col:
                with st.container(border=True):
                    st.markdown('#### ⏱️ Experience & Education Calibration')
                    cand_exp = float(data.get("candidate_experience", 0))
                    req_exp = float(data.get("required_experience", 0))
                    gap = float(data.get("experience_gap", 0))

                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">'
                        f'<span><strong>Candidate Tenure:</strong> {cand_exp:.1f} yrs</span>'
                        f'<span><strong>Required:</strong> {req_exp:.1f} yrs</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    max_exp_scale = max(1.0, max(cand_exp, req_exp) * 1.2)
                    st.progress(min(1.0, cand_exp / max_exp_scale))

                    gap_badge = (
                        f'<span class="skill-pill pill-match">✓ Meets Requirement (Gap: {gap:.1f} yrs)</span>'
                        if gap <= 0
                        else f'<span class="skill-pill pill-missing">⚠️ Experience Gap: {gap:.1f} yrs</span>'
                    )
                    st.markdown(f'<div style="margin:0.6rem 0;">{gap_badge}</div>', unsafe_allow_html=True)
                    st.markdown(f"**Experience Status:** {status_label(data.get('experience_status'))}")
                    st.markdown(f"**Education Assessment:** {status_label(data.get('education_status'))}")

        # TAB 2: AI RESUME TAILOR
        with tabs[1]:
            st.markdown('### 🎯 AI Resume Tailor & Bullet Optimizer')
            st.write('Directly align your resume with the target job criteria to elevate ATS ranking and interview callbacks.')

            tailoring = data.get('tailoring_suggestions', {})
            if not tailoring:
                st.info('Tailoring suggestions are not available for this record.')
            else:
                target_title = tailoring.get('target_title', 'Target Role')
                st.markdown(
                    f'<div style="padding:10px 16px;border-radius:12px;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);margin-bottom:1.2rem;">'
                    f'Target Role Identified: <strong>{target_title}</strong>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # 1. Professional Summary
                st.markdown('#### 1. Tailored Professional Summary')
                st.caption('Drop this 3-sentence role-aligned summary at the top of your resume:')
                st.code(tailoring.get('tailored_summary', ''), language='text')

                # 2. STAR Bullets
                st.markdown('#### 2. High-Impact STAR Bullet Points (Tailored for Missing Skills)')
                st.caption('Insert these production-ready bullet points under your work experience or project achievements:')
                star_bullets = tailoring.get('star_bullet_points', [])
                if star_bullets:
                    for idx, bullet in enumerate(star_bullets, start=1):
                        with st.container(border=True):
                            b1, b2 = st.columns([3, 1])
                            b1.markdown(f"**#{idx} Skill Focus:** `{bullet.get('skill', '')}`")
                            b2.markdown('<span class="skill-pill pill-alias">⚡ STAR Formula</span>', unsafe_allow_html=True)
                            st.code(bullet.get('bullet_point', ''), language='text')
                else:
                    st.success('🎉 You already match all core required skills! No supplemental skill bullets needed.')

                # 3. Categorized Skills Section
                st.markdown('#### 3. Optimized ATS Skills Block')
                st.caption('Ensure ATS keyword extractors parse all required skills by updating your skills block:')
                skills_sec = tailoring.get('skills_section', {})
                st.code(skills_sec.get('formatted_copy_paste', ''), language='text')

                # 4. Strategic Placement
                st.markdown('#### 4. Strategic Keyword Placement Guide')
                for step in tailoring.get('placement_strategy', []):
                    with st.expander(f"📍 {step.get('section', 'Section')}: {step.get('action', '')}", expanded=False):
                        st.write(f"**Why this matters:** {step.get('reason', '')}")

        # TAB 3: ATS RESUME HEALTH CHECK
        with tabs[2]:
            st.markdown('### 🩺 ATS Resume Health & Parseability Audit')
            st.caption('Evaluates how cleanly applicant tracking systems parse your contact channels, formatting, metrics, and active verbs.')

            health = data.get('resume_health', {})
            if not health:
                st.info('Resume health audit is not available for this record.')
            else:
                score = health.get('health_score', 0)
                grade = health.get('grade', 'N/A')

                h_col1, h_col2, h_col3 = st.columns([1.2, 1.4, 1.4], gap='large')
                with h_col1:
                    st.markdown(render_grade_circle(grade, score), unsafe_allow_html=True)
                with h_col2:
                    st.markdown('**Diagnostics Summary:**')
                    st.write(f"• Word count: **{health.get('word_count', 0)}** words (~{health.get('page_estimate', 1)} page(s))")
                    st.write(f"• Quantifiable metrics detected: **{len(health.get('metrics_found', []))}**")
                    st.write(f"• Strong action verbs detected: **{len(health.get('action_verbs_found', []))}**")
                    weak_phr = health.get('weak_phrases_found', [])
                    if weak_phr:
                        st.write(f"• ⚠️ Passive phrases flagged: **{len(weak_phr)}**")
                    else:
                        st.write("• ✅ Passive phrases flagged: **0**")
                with h_col3:
                    st.markdown('**Category Breakdown:**')
                    bd = health.get('score_breakdown', {})
                    st.write(f"• Contact Channels: **{bd.get('contact_info', 0)}/25**")
                    st.write(f"• Section Structure: **{bd.get('section_structure', 0)}/30**")
                    st.write(f"• Measurable Metrics: **{bd.get('quantifiable_metrics', 0)}/25**")
                    st.write(f"• Action Verb Strength: **{bd.get('action_verb_strength', 0)}/20**")

                st.write('')
                st.divider()

                # Contact Channels Verification
                st.markdown('#### 📇 Contact Channels Verification')
                contact = health.get('contact_info', {})
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    c_mail = '✓ ' + contact['email'] if contact.get('email') else '✕ Missing'
                    p_type = 'match' if contact.get('email') else 'missing'
                    st.markdown(f'<span class="skill-pill pill-{p_type}">Email: {c_mail}</span>', unsafe_allow_html=True)
                with c2:
                    c_phone = '✓ ' + contact['phone'] if contact.get('phone') else '✕ Missing'
                    p_type = 'match' if contact.get('phone') else 'missing'
                    st.markdown(f'<span class="skill-pill pill-{p_type}">Phone: {c_phone}</span>', unsafe_allow_html=True)
                with c3:
                    c_li = '✓ LinkedIn Present' if contact.get('linkedin') else '⚠️ Missing LinkedIn'
                    p_type = 'match' if contact.get('linkedin') else 'preferred'
                    st.markdown(f'<span class="skill-pill pill-{p_type}">{c_li}</span>', unsafe_allow_html=True)
                with c4:
                    c_gh = '✓ Portfolio Present' if contact.get('github') or contact.get('portfolio') else '• Portfolio Optional'
                    p_type = 'match' if contact.get('github') or contact.get('portfolio') else 'neutral'
                    st.markdown(f'<span class="skill-pill pill-{p_type}">{c_gh}</span>', unsafe_allow_html=True)

                st.write('')

                # Standard Section Headers
                st.markdown('#### 📑 Standard ATS Section Headers')
                s_detected = health.get('sections_detected', [])
                sec_cols = st.columns(6)
                all_core = ['experience', 'education', 'skills', 'projects', 'summary', 'certifications']
                for c, s_name in zip(sec_cols, all_core):
                    is_present = s_name in s_detected
                    p_type = 'match' if is_present else 'neutral'
                    with c:
                        st.markdown(
                            f'<span class="skill-pill pill-{p_type}">{"✓" if is_present else "•"} {s_name.title()}</span>',
                            unsafe_allow_html=True
                        )

                st.write('')

                # Quantifiable Metrics & Action Verbs
                st.markdown('#### 📈 Measurable Metrics & Action Verbs')
                m_left, m_right = st.columns(2, gap='large')
                with m_left:
                    st.markdown('**Quantifiable Impact Metrics Detected:**')
                    metrics = health.get('metrics_found', [])
                    if metrics:
                        st.markdown(render_skill_pills(metrics, 'match'), unsafe_allow_html=True)
                    else:
                        st.warning('No measurable metrics detected! Add percentages, dollar savings, or scale numbers.')
                with m_right:
                    st.markdown('**Strong Action Verbs Used:**')
                    verbs = health.get('action_verbs_found', [])
                    if verbs:
                        st.markdown(render_skill_pills(verbs[:10], 'alias'), unsafe_allow_html=True)
                    else:
                        st.info('No strong action verbs identified.')

                st.write('')

                # Actionable Checklist
                st.markdown('#### 📋 Actionable ATS Health Checklist')
                checklist = health.get('checklist', {})
                crit_list = checklist.get('critical', [])
                if crit_list:
                    for crit in crit_list:
                        st.error(f"🔴 **Critical:** {crit}")

                warn_list = checklist.get('warnings', [])
                if warn_list:
                    for warn in warn_list:
                        st.warning(f"🟡 **Improvement:** {warn}")

                pass_list = checklist.get('passed', [])
                if pass_list:
                    with st.expander(f"🟢 Passed Standards ({len(pass_list)})", expanded=False):
                        for p in pass_list:
                            st.write(f"✅ {p}")

        # TAB 4: REQUIREMENT EVIDENCE
        with tabs[3]:
            st.markdown('### 📋 Structured Requirement Evidence')
            requirements = data.get('requirement_analysis', [])
            if requirements:
                for requirement in requirements:
                    status = requirement.get('status', 'unknown').title()
                    score = float(requirement.get('score', 0))
                    name = requirement.get("name", requirement.get("canonical", "Requirement"))

                    badge_class = 'pill-match' if status.lower() == 'met' else 'pill-alias' if 'partial' in status.lower() else 'pill-missing'
                    title_md = f"**{name}**"

                    with st.expander(f"{status}: {name}", expanded=status.lower() == 'missing'):
                        st.markdown(
                            f'<div style="display:flex;gap:8px;margin-bottom:0.6rem;">'
                            f'<span class="skill-pill {badge_class}">{status}</span>'
                            f'<span class="skill-pill pill-neutral">Category: {requirement.get("category", "Unknown")}</span>'
                            f'<span class="skill-pill pill-neutral">Score: {score:.0f}%</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.progress(min(1.0, max(0.0, score / 100.0)))
                        st.markdown(f"**Evidence from Resume:**")
                        st.info(requirement.get("evidence", "No explicit textual evidence identified in resume."))
            else:
                st.info('Requirement-level evidence was not returned in this API response.')

        # TAB 5: SEMANTIC & COMPETENCIES
        with tabs[4]:
            st.markdown('### 🔍 Semantic Alignment & Competencies')
            s_left, s_right = st.columns(2, gap='large')
            with s_left:
                with st.container(border=True):
                    st.markdown('#### 🤝 Soft Competencies')
                    st.markdown('**Matched Competencies:**')
                    st.markdown(render_skill_pills(data.get('matched_competencies', []), 'match'), unsafe_allow_html=True)
                    st.markdown('**Missing Competencies:**')
                    st.markdown(render_skill_pills(data.get('missing_competencies', []), 'missing'), unsafe_allow_html=True)

            with s_right:
                with st.container(border=True):
                    st.markdown('#### 🔑 Job Keywords')
                    st.markdown('**Matched Keywords:**')
                    st.markdown(render_skill_pills(data.get('matched_keywords', []), 'alias'), unsafe_allow_html=True)
                    st.markdown('**Missing Keywords:**')
                    st.markdown(render_skill_pills(data.get('missing_keywords', []), 'missing'), unsafe_allow_html=True)

            st.write('')
            with st.container(border=True):
                st.markdown('#### 📈 Calibrated TF-IDF Text Similarity')
                tfidf_val = float(data.get("tfidf_similarity", 0))
                st.markdown(
                    f'<div style="font-size:2rem;font-weight:800;color:#38bdf8;">{tfidf_val:.1%}</div>',
                    unsafe_allow_html=True
                )
                st.progress(min(1.0, max(0.0, tfidf_val)))
                st.caption(
                    'Evaluated through a calibrated logistic curve mapping realistic corpus overlap (0.05–0.40 cosine) '
                    'to a balanced score, serving as a supporting signal without masking missing technical requirements.'
                )

        # TAB 6: ATS NOTES & INSIGHTS
        with tabs[5]:
            st.markdown('### 💡 ATS Notes & Contextual Alignment')
            explanations = data.get('explanations', [])
            if explanations:
                for exp in explanations:
                    st.markdown(
                        f'<div style="padding:10px 14px;border-radius:10px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);margin-bottom:0.6rem;">'
                        f'💡 {exp}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info('No additional ATS explanations were returned.')


# ==============================================================================
# MODE 2: AUTO-JOB RECOMMENDER (FIND BEST MATCHING JOBS)
# ==============================================================================
elif main_nav == '🚀 Mode 2: Auto-Job Recommender (6,200+ Live Jobs)':
    st.markdown('### 🚀 Auto-Job Recommender & Opportunity Finder')
    st.write(
        'Upload your resume once, select your target category and preferences, and let ResumeMatch ATS '
        'scan and rank the highest-scoring job opportunities from Supabase.'
    )

    rec_resume = st.file_uploader(
        'Candidate Resume (PDF, DOCX, TXT):',
        type=['pdf', 'docx', 'txt'],
        key='rec_resume_uploader',
        help='Supported formats: PDF, DOCX, and TXT with magic-byte validation.',
    )
    if rec_resume:
        st.session_state['saved_resume_tuple'] = (rec_resume.name, rec_resume.getvalue(), rec_resume.type)
        st.markdown(
            f'<div style="padding:6px 12px;border-radius:8px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);color:#34d399;font-size:0.85rem;font-weight:600;">'
            f'✓ {rec_resume.name} loaded ({rec_resume.size / 1024:.0f} KB)</div>',
            unsafe_allow_html=True
        )
    elif st.session_state.get('saved_resume_tuple'):
        saved_name = st.session_state['saved_resume_tuple'][0]
        st.markdown(
            f'<div style="padding:6px 12px;border-radius:8px;background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;font-size:0.85rem;font-weight:600;">'
            f'ℹ️ Using resume uploaded earlier: {saved_name}</div>',
            unsafe_allow_html=True
        )

    with st.container(border=True):
        st.markdown('**Filter & Search Options**')
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            rec_cat_options = ['All']
            try:
                kw_res = requests.get(f'{API_URL}/supabase/keywords', timeout=4)
                if kw_res.ok:
                    rec_cat_options.extend(kw_res.json().get('keywords', []))
            except Exception:
                pass
            chosen_cat = st.selectbox('Category / Job Role:', options=rec_cat_options, key='recom_cat')
            search_keywords = st.text_input(
                'Title, Company, or Keywords (optional):',
                placeholder='e.g. Remote, Power BI, Google, Python',
                key='recom_q'
            )

        with f_col2:
            exp_map = {
                'All Experience Levels': 'all',
                '0-2 Years (Entry Level / Junior)': '0-2',
                '2-5 Years (Mid-Level)': '2-5',
                '5+ Years (Senior / Lead)': '5+'
            }
            exp_choice = st.selectbox('Experience Level:', options=list(exp_map.keys()), key='recom_exp')

            time_map = {
                'All Time': 'all',
                'Past 24 Hours': '24h',
                'Past 3 Days': '3d',
                'Past 7 Days': '7d',
                'Past 30 Days': '30d'
            }
            time_choice = st.selectbox('Time Posted:', options=list(time_map.keys()), key='recom_time')

        rec_btn_col1, rec_btn_col2 = st.columns([2, 1])
        with rec_btn_col1:
            top_n = st.slider('Number of Top Matches to Return:', min_value=3, max_value=25, value=10, key='recom_top_n')
        with rec_btn_col2:
            st.write('')
            st.write('')
            find_btn = st.button('🚀 Find Matching Jobs', type='primary', use_container_width=True)

    if find_btn:
        active_resume_tuple = (
            (rec_resume.name, rec_resume.getvalue(), rec_resume.type)
            if rec_resume
            else st.session_state.get('saved_resume_tuple')
        )
        if not active_resume_tuple:
            st.warning('⚠️ Please upload a resume file above to scan matching jobs.')
        else:
            try:
                with st.spinner(f'Scanning and scoring jobs in category "{chosen_cat}" from Supabase...'):
                    rec_response = requests.post(
                        f'{API_URL}/supabase/recommend',
                        files={'resume_file': active_resume_tuple},
                        data={
                            'category': chosen_cat,
                            'query': search_keywords,
                            'time_frame': time_map[time_choice],
                            'experience_level': exp_map[exp_choice],
                            'limit': top_n,
                        },
                        timeout=90
                    )
                if rec_response.ok:
                    st.session_state['recommendations_data'] = rec_response.json()
                    st.success('Job scanning and ranking complete!')
                else:
                    st.error(api_error(rec_response))
            except requests.RequestException:
                st.error('Could not connect to the backend server. Ensure Uvicorn is running.')

    if 'recommendations_data' in st.session_state:
        rec_data = st.session_state['recommendations_data']
        recs = rec_data.get('recommendations', [])
        total_scanned = rec_data.get('total_scanned', 0)
        total_matched = rec_data.get('total_matched', 0)

        st.write('')
        st.markdown('---')

        # Stat cards row
        m_col1, m_col2, m_col3, m_col4 = st.columns([1, 1, 1, 1.4])
        with m_col1:
            st.markdown(
                f'<div class="stat-card"><div class="stat-title">Jobs Scanned</div>'
                f'<div class="stat-value">{total_scanned:,}</div>'
                f'<div class="stat-sub">Supabase live database</div></div>',
                unsafe_allow_html=True
            )
        with m_col2:
            st.markdown(
                f'<div class="stat-card"><div class="stat-title">Matches Found</div>'
                f'<div class="stat-value">{total_matched:,}</div>'
                f'<div class="stat-sub">Category & filters met</div></div>',
                unsafe_allow_html=True
            )
        if recs:
            top_score = recs[0]['overall_score']
            with m_col3:
                st.markdown(
                    f'<div class="stat-card"><div class="stat-title">Top ATS Match</div>'
                    f'<div class="stat-value" style="color:#34d399;">{top_score:.1f}%</div>'
                    f'<div class="stat-sub">{recs[0]["company"]}</div></div>',
                    unsafe_allow_html=True
                )
            with m_col4:
                st.write('')
                st.download_button(
                    label='📥 Export to CSV (Job Tracker)',
                    data=build_recommendations_csv(recs),
                    file_name='ATS_Job_Application_Tracker.csv',
                    mime='text/csv',
                    use_container_width=True,
                    help='Download top ranked job matches as a spreadsheet tracker with links and application statuses.'
                )

        if not recs:
            st.info('No jobs met the selected experience or time criteria. Try selecting "All Experience Levels" or "All Time".')
        else:
            st.markdown(f'### Top {len(recs)} Ranked Job Opportunities')
            for idx, r in enumerate(recs, start=1):
                score = r['overall_score']
                score_color = '#10b981' if score >= 75 else '#0ea5e9' if score >= 55 else '#f59e0b' if score >= 40 else '#f43f5e'
                desc_badge = '🟢 Full JD' if r.get('has_full_description') else '📋 Enriched Summary'

                with st.container(border=True):
                    head_col1, head_col2 = st.columns([3.2, 1.2])
                    with head_col1:
                        st.markdown(f"### #{idx} {r['title']}")
                        st.markdown(
                            f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:0.6rem;">'
                            f'<span class="skill-pill pill-neutral">🏢 {r["company"]}</span>'
                            f'<span class="skill-pill pill-neutral">📍 {r["location"]}</span>'
                            f'<span class="skill-pill pill-alias">🕒 {r.get("posted_label", "Recent")}</span>'
                            f'<span class="skill-pill pill-match">{desc_badge}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with head_col2:
                        st.markdown(
                            f'<div style="text-align:right;">'
                            f'<div style="font-size:2.2rem;font-weight:800;color:{score_color};line-height:1;">{score:.1f}%</div>'
                            f'<div style="font-size:0.75rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">{r["recommendation"]}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    # Experience bar
                    c_exp = r.get('candidate_experience', 0)
                    r_exp = r.get('required_experience', 0)
                    e_gap = r.get('experience_gap', 0)
                    st.markdown(
                        f'<div style="font-size:0.85rem;color:#cbd5e1;margin-bottom:0.4rem;">'
                        f'Candidate Experience: <strong>{c_exp:.1f} yrs</strong> | '
                        f'Required: <strong>{r_exp:.1f} yrs</strong> | '
                        f'Gap: <strong>{e_gap:.1f} yrs</strong>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Skills pills
                    st.markdown('**Matched Skills:**')
                    st.markdown(render_skill_pills(r.get('matched_skills', []), 'match'), unsafe_allow_html=True)
                    if r.get('missing_skills'):
                        st.markdown('**Missing Skills:**')
                        st.markdown(render_skill_pills(r.get('missing_skills', []), 'missing'), unsafe_allow_html=True)

                    st.write('')

                    # Action buttons
                    b_col1, b_col2 = st.columns([1.2, 1.2])
                    with b_col1:
                        inspect_btn = st.button(
                            '🔍 Inspect Full Match',
                            key=f'inspect_rec_{r["job_id"]}_{idx}',
                            use_container_width=True,
                            type='secondary',
                            help='Open complete requirement breakdown, radar chart, ATS health, and report download.'
                        )
                        if inspect_btn:
                            st.session_state['pending_inspect_job'] = r
                            st.rerun()

                    with b_col2:
                        if r.get('link'):
                            st.link_button('🔗 Apply on LinkedIn', r['link'], use_container_width=True)
                        else:
                            st.caption('No direct application URL')

                    # Full Job Description Viewer (Uncut)
                    full_desc = r.get('description', '')
                    word_cnt = len(full_desc.split()) if full_desc else 0
                    with st.expander(f'📄 Full Job Description ({word_cnt:,} words)', expanded=False):
                        st.text_area(
                            f'Complete Job Description for {r["title"]}:',
                            value=full_desc,
                            height=300,
                            disabled=True,
                            key=f'full_jd_view_{r["job_id"]}_{idx}'
                        )

                    tailor_info = r.get('tailoring_suggestions')
                    if tailor_info and tailor_info.get('star_bullet_points'):
                        with st.expander('🎯 Tailored Resume Bullet Points for This Job', expanded=False):
                            st.caption(f"Role target: **{tailor_info.get('target_title', r['title'])}**")
                            for b in tailor_info.get('star_bullet_points', [])[:3]:
                                st.code(f"[{b.get('skill')}] {b.get('bullet_point')}", language='text')
