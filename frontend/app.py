from io import BytesIO
import os

import requests
import streamlit as st
from docx import Document


API_URL = os.getenv('MATCHER_API_URL', 'http://127.0.0.1:8000').rstrip('/')
st.set_page_config(
    page_title='ResumeMatch ATS',
    page_icon='ATS',
    layout='wide',
    initial_sidebar_state='collapsed',
)

st.markdown('''<style>
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:4rem}
.hero{padding:1.2rem 0 1.2rem}.hero h1{font-size:2.6rem;margin:0}
.hero p{font-size:1.1rem;opacity:.7}.score{font-size:4rem;font-weight:800;text-align:center}
.muted{text-align:center;opacity:.7}.good{font-weight:700;text-align:center;font-size:1.2rem}
</style>''', unsafe_allow_html=True)


def api_error(response):
    try:
        detail = response.json().get('detail')
        if isinstance(detail, str) and detail:
            return detail
    except (ValueError, requests.RequestException):
        pass
    return f'Backend returned status {response.status_code}.'


def display_items(items):
    return ', '.join(items) if items else 'None identified'


def status_label(status):
    return status or 'Not available'


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
    document.add_paragraph('Matched: ' + display_items(data.get('matched_skills', [])))
    document.add_paragraph('To improve: ' + display_items(data.get('missing_skills', [])))
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

    output = BytesIO()
    document.save(output)
    return output.getvalue()


st.markdown(
    '<div class="hero"><h1>ResumeMatch ATS</h1>'
    '<p>Upload one resume, compare it with a job description, and inspect the evidence behind the score.</p></div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.subheader('Start an analysis')
    input_col, job_col = st.columns(2, gap='large')
    with input_col:
        resume = st.file_uploader(
            'Resume file',
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=False,
            help='Supported formats: PDF, DOCX, and TXT. Maximum size is controlled by the API.',
        )
        if resume:
            st.success(f'{resume.name} ready ({resume.size / 1024:.0f} KB)')
        else:
            st.caption('Choose one resume file to continue.')
    with job_col:
        jd = st.text_area(
            'Job description',
            height=220,
            placeholder='Paste the complete job description here...',
            help='Include responsibilities, required skills, experience, and education details for the most useful analysis.',
        )
        if jd.strip():
            st.caption(f'{len(jd.split()):,} words')
        else:
            st.caption('Paste the job description to continue.')

    action_col, clear_col, status_col = st.columns([2, 1, 2])
    ready = bool(resume and jd.strip())
    with action_col:
        analyze = st.button('Analyze resume', type='primary', use_container_width=True, disabled=not ready)
    with clear_col:
        clear = st.button('Clear results', use_container_width=True, disabled='result' not in st.session_state)
    with status_col:
        try:
            health = requests.get(f'{API_URL}/health', timeout=3)
            if health.ok:
                st.success('Backend connected')
            else:
                st.warning('Backend needs attention')
        except requests.RequestException:
            st.warning('Backend unavailable')

if clear:
    st.session_state.pop('result', None)
    st.session_state.pop('resume_name', None)
    st.rerun()

if analyze:
    try:
        with st.spinner('Extracting resume evidence and matching requirements...'):
            response = requests.post(
                f'{API_URL}/match/file',
                files={'resume_file': (resume.name, resume.getvalue(), resume.type)},
                data={'job_description': jd},
                timeout=90,
            )
        if not response.ok:
            st.error(api_error(response))
        else:
            st.session_state['result'] = response.json()
            st.session_state['resume_name'] = resume.name
            st.success('Analysis complete.')
    except requests.RequestException:
        st.error(f'Could not connect to the matching API at {API_URL}. Start the backend and try again.')
    except ValueError:
        st.error('The backend returned an invalid response. Check the API logs for details.')


if 'result' in st.session_state:
    data = st.session_state['result']
    scores = data.get('component_scores', {})
    overall = float(data.get('overall_score', 0))

    st.divider()
    score_col, summary_col = st.columns([1, 2], gap='large')
    with score_col:
        st.subheader('ATS match score')
        st.markdown(f'<div class="score">{overall:.1f}%</div>', unsafe_allow_html=True)
        st.progress(min(1, max(0, overall / 100)))
    with summary_col:
        st.subheader(data.get('recommendation', 'Match result'))
        st.write('Overall fit based on explicit evidence, experience, education, competencies, keywords, and text similarity.')
        if st.session_state.get('resume_name'):
            st.caption(f'Resume analyzed: {st.session_state["resume_name"]}')
        export_col, _ = st.columns([1, 2])
        with export_col:
            st.download_button(
                'Download DOCX report',
                data=build_docx_report(data, st.session_state.get('resume_name', 'resume')),
                file_name='resume-match-report.docx',
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True,
            )

    tabs = st.tabs(['Overview', 'Requirements', 'Evidence', 'ATS notes'])
    with tabs[0]:
        st.subheader('Score breakdown')
        labels = [
            ('Skills', 'skills'), ('Experience', 'experience'), ('Education', 'education'),
            ('Competencies', 'competencies'), ('Keywords', 'keywords'), ('Similarity', 'tfidf'),
        ]
        score_columns = st.columns(6)
        for column, (label, key) in zip(score_columns, labels):
            column.metric(label, f'{float(scores.get(key, 0)):.1f}%')

        left, right = st.columns(2, gap='large')
        with left:
            st.subheader('Skills')
            st.write('**Matched:** ' + display_items(data.get('matched_skills', [])))
            st.write('**To improve:** ' + display_items(data.get('missing_skills', [])))
            st.caption(
                f'Exact: {len(data.get("exact_skill_matches", []))} | '
                f'Alias: {len(data.get("alias_skill_matches", []))} | '
                f'Partial: {len(data.get("partial_skill_matches", []))} | '
                f'Related: {len(data.get("related_skill_matches", []))}'
            )
        with right:
            st.subheader('Experience and education')
            st.write(f'**Candidate experience:** {float(data.get("candidate_experience", 0)):g} years')
            st.write(f'**Required experience:** {float(data.get("required_experience", 0)):g} years')
            st.write(f'**Gap:** {float(data.get("experience_gap", 0)):g} years')
            st.info(status_label(data.get('experience_status')))
            st.write('**Education:** ' + status_label(data.get('education_status')))

    with tabs[1]:
        requirements = data.get('requirement_analysis', [])
        st.subheader('Requirement evidence')
        if requirements:
            for requirement in requirements:
                status = requirement.get('status', 'unknown').title()
                score = float(requirement.get('score', 0))
                title = f'{status}: {requirement.get("name", requirement.get("canonical", "Requirement"))}'
                with st.expander(title, expanded=status.lower() == 'missing'):
                    st.progress(min(1, max(0, score / 100)))
                    st.write(f'**Category:** {requirement.get("category", "Unknown")}')
                    st.write(f'**Evidence:** {requirement.get("evidence", "No evidence provided.")}')
                    st.caption(f'Match type: {requirement.get("match_type", "unknown")} | Score: {score:.0f}%')
        else:
            st.info('Requirement-level evidence is not included in this API response yet.')

    with tabs[2]:
        left, right = st.columns(2, gap='large')
        with left:
            st.subheader('Competencies')
            st.write('**Matched:** ' + display_items(data.get('matched_competencies', [])))
            st.write('**Missing:** ' + display_items(data.get('missing_competencies', [])))
        with right:
            st.subheader('Job keywords')
            st.write('**Matched:** ' + display_items(data.get('matched_keywords', [])))
            st.write('**Missing:** ' + display_items(data.get('missing_keywords', [])))
        st.subheader('Text similarity')
        st.write(f'{float(data.get("tfidf_similarity", 0)):.1%}')
        st.caption('Similarity supports the result but does not prove that a missing skill is present.')

    with tabs[3]:
        st.subheader('ATS analysis')
        explanations = data.get('explanations', [])
        if explanations:
            for explanation in explanations:
                st.write(f'- {explanation}')
        else:
            st.info('No additional explanations were returned.')