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


st.markdown(
    '<div class="hero"><h1>ResumeMatch ATS</h1>'
    '<p>Explainable resume matching & real-time career job discovery engine powered by Supabase.</p></div>',
    unsafe_allow_html=True,
)

main_nav = st.radio(
    'Workflow Mode:',
    ['🎯 Match Specific Job', '🚀 Auto-Job Recommender (Find Best Matching Jobs)'],
    horizontal=True,
    key='main_nav_mode'
)

st.divider()

# ==============================================================================
# MODE 1: MATCH SPECIFIC JOB
# ==============================================================================
if main_nav == '🎯 Match Specific Job':
    with st.container(border=True):
        st.subheader('Start a single match analysis')
        input_col, job_col = st.columns(2, gap='large')
        with input_col:
            resume = st.file_uploader(
                'Resume file',
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=False,
                key='single_resume_uploader',
                help='Supported formats: PDF, DOCX, and TXT.',
            )
            if resume:
                st.session_state['saved_resume_tuple'] = (resume.name, resume.getvalue(), resume.type)
                st.success(f'{resume.name} ready ({resume.size / 1024:.0f} KB)')
            else:
                st.caption('Choose one resume file to continue.')

        with job_col:
            source_mode = st.radio(
                'Job Source',
                ['📋 Paste Description', '🗄️ Supabase Role Database'],
                horizontal=True,
                help='Choose whether to manually paste a job description or pick from the Supabase database.'
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
                        f'Select Target Role ({len(fetched_jobs)} matches found):',
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
                        help='Description auto-loaded from Supabase database. You can adjust it before analyzing if needed.',
                    )
                    desc_type = "🟢 Full Description" if chosen_job.get('has_full_description') else "📋 Brief Summary (enriched with database skills & experience)"
                    st.caption(
                        f"🏢 **{chosen_job['company']}** | 📍 **{chosen_job['location']}** | 📝 {len(jd.split()):,} words | {desc_type}"
                    )
                    if chosen_job.get('link'):
                        st.markdown(f"[🔗 View / Apply on LinkedIn]({chosen_job['link']})")
                else:
                    st.info('No matching jobs found in Supabase. Try a different search term or category.')
                    jd = ''
            else:
                jd = st.text_area(
                    'Job description',
                    height=220,
                    placeholder='Paste the complete job description here...',
                    help='Include responsibilities, required skills, experience, and education details for the most useful analysis.',
                    key='jd_paste_text'
                )
                if jd.strip():
                    st.caption(f'{len(jd.split()):,} words')
                else:
                    st.caption('Paste the job description to continue.')

        action_col, clear_col, status_col = st.columns([2, 1, 2])
        with action_col:
            analyze = st.button('Analyze resume', type='primary', use_container_width=True)
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

        with st.expander('📜 View Past Match History', expanded=False):
            try:
                matches_res = requests.get(f'{API_URL}/matches', timeout=3)
                if matches_res.ok and matches_res.json():
                    past_matches = matches_res.json()
                    st.caption(f'Found {len(past_matches)} recent analysis record(s).')
                    match_options = {
                        f"#{m['match_id']} | {m['job_title']} ({m['resume_name']}) - {m['overall_score']:.1f}% [{m['recommendation']}] - {m['created_at']}": m['match_id']
                        for m in past_matches
                    }
                    selected_label = st.selectbox('Select a previous match to view details:', options=list(match_options.keys()))
                    if st.button('Load Match Details', use_container_width=False):
                        sel_id = match_options[selected_label]
                        detail_res = requests.get(f'{API_URL}/match/{sel_id}', timeout=5)
                        if detail_res.ok:
                            st.session_state['result'] = detail_res.json()
                            st.session_state['resume_name'] = next((m['resume_name'] for m in past_matches if m['match_id'] == sel_id), 'resume')
                            st.success(f"Loaded match #{sel_id} successfully!")
                            st.rerun()
                        else:
                            st.error('Could not load match details from server.')
                else:
                    st.info('No past matches found in the database yet.')
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
                with st.spinner('Extracting resume evidence and matching requirements...'):
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
                    st.success('Analysis complete.')
                    st.rerun()
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

        tabs = st.tabs(['Overview', '🎯 AI Resume Tailor', '🩺 ATS Health Check', 'Requirements', 'Evidence', 'ATS notes'])
        with tabs[0]:
            st.subheader('Score breakdown')
            labels = [
                ('Skills', 'skills'), ('Experience', 'experience'), ('Education', 'education'),
                ('Competencies', 'competencies'), ('Keywords', 'keywords'), ('Title & level', 'title'),
                ('Location & authorization', 'context'), ('Similarity', 'tfidf'),
            ]
            for start in range(0, len(labels), 4):
                score_columns = st.columns(4)
                for column, (label, key) in zip(score_columns, labels[start:start + 4]):
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
            st.subheader('🎯 AI Resume Tailor & Bullet Optimizer')
            st.caption('Tailor your resume specifically for this target role to maximize ATS ranking and interview callbacks.')

            tailoring = data.get('tailoring_suggestions', {})
            if not tailoring:
                st.info('Tailoring suggestions are not available for this match.')
            else:
                target_title = tailoring.get('target_title', 'Target Role')
                st.markdown(f"### Target Role: **{target_title}**")

                # 1. Tailored Professional Summary
                st.markdown("#### 1. Tailored Professional Summary")
                st.write("Replace or update your resume summary section with this role-aligned statement:")
                st.code(tailoring.get('tailored_summary', ''), language='text')

                # 2. STAR-Method Bullet Points for Missing Skills
                st.markdown("#### 2. High-Impact STAR Bullet Points (Tailored for Missing Skills)")
                st.write(
                    "Insert these production-ready bullet points under your work experience or projects. "
                    "Each bullet is engineered using the **STAR formula** (*Action Verb + Context + Measurable Impact*):"
                )

                star_bullets = tailoring.get('star_bullet_points', [])
                if star_bullets:
                    for idx, bullet in enumerate(star_bullets, start=1):
                        with st.container(border=True):
                            b_head1, b_head2 = st.columns([3, 1])
                            b_head1.markdown(f"**#{idx} Skill Focus:** `{bullet.get('skill', '')}`")
                            b_head2.caption(f"⚡ {bullet.get('formula', 'STAR Method')}")
                            st.code(bullet.get('bullet_point', ''), language='text')
                else:
                    st.success("🎉 You matched all core skills! No critical skill bullet points needed.")

                # 3. Categorized ATS Skills Section
                st.markdown("#### 3. Optimized ATS Skills Block")
                st.write("Ensure ATS keyword extractors parse all required skills by updating your skills block:")
                skills_sec = tailoring.get('skills_section', {})
                st.code(skills_sec.get('formatted_copy_paste', ''), language='text')

                # 4. Placement Strategy
                st.markdown("#### 4. Keyword Placement Strategy")
                for step in tailoring.get('placement_strategy', []):
                    with st.expander(f"📍 {step.get('section', 'Section')}: {step.get('action', '')}", expanded=False):
                        st.write(f"**Why this matters:** {step.get('reason', '')}")

        with tabs[2]:
            st.subheader('🩺 ATS Resume Health & Parseability Audit')
            st.caption('Evaluates how cleanly applicant tracking systems parse your contact information, formatting, metrics, and active verbs.')

            health = data.get('resume_health', {})
            if not health:
                st.info('Resume health audit is not available for this record.')
            else:
                h_col1, h_col2, h_col3 = st.columns([1, 2, 2])
                score = health.get('health_score', 0)
                grade = health.get('grade', 'N/A')

                with h_col1:
                    st.metric('Parseability Health', f"{score}/100", f"Grade {grade}")
                    st.progress(min(1.0, max(0.0, score / 100.0)))

                with h_col2:
                    st.write("**Diagnostics Summary:**")
                    st.write(f"• Word count: **{health.get('word_count', 0)}** words (~{health.get('page_estimate', 1)} page(s))")
                    st.write(f"• Quantifiable metrics detected: **{len(health.get('metrics_found', []))}**")
                    st.write(f"• Strong action verbs detected: **{len(health.get('action_verbs_found', []))}**")
                    weak_phr = health.get('weak_phrases_found', [])
                    if weak_phr:
                        st.write(f"• ⚠️ Passive phrases flagged: **{len(weak_phr)}**")
                    else:
                        st.write("• ✅ Passive phrases flagged: **0**")

                with h_col3:
                    st.write("**Score Breakdown:**")
                    bd = health.get('score_breakdown', {})
                    st.write(f"• Contact Info: **{bd.get('contact_info', 0)}/25**")
                    st.write(f"• Section Structure: **{bd.get('section_structure', 0)}/30**")
                    st.write(f"• Measurable Metrics: **{bd.get('quantifiable_metrics', 0)}/25**")
                    st.write(f"• Action Verb Strength: **{bd.get('action_verb_strength', 0)}/20**")

                st.divider()

                # Contact Information Detected
                st.markdown("#### 📇 Contact Information Verification")
                contact = health.get('contact_info', {})
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**Email:** {'✅ ' + contact['email'] if contact.get('email') else '❌ Missing'}")
                c2.write(f"**Phone:** {'✅ ' + contact['phone'] if contact.get('phone') else '❌ Missing'}")
                c3.write(f"**LinkedIn:** {'✅ Yes' if contact.get('linkedin') else '⚠️ Missing'}")
                c4.write(f"**GitHub / Web:** {'✅ Yes' if contact.get('github') or contact.get('portfolio') else '⚪ Optional'}")

                # Standard Section Headers
                st.markdown("#### 📑 Standard ATS Section Headers")
                s_detected = health.get('sections_detected', [])
                sec_cols = st.columns(6)
                all_core = ['experience', 'education', 'skills', 'projects', 'summary', 'certifications']
                for c, s_name in zip(sec_cols, all_core):
                    is_present = s_name in s_detected
                    c.write(f"{'✅' if is_present else '⚪'} {s_name.title()}")

                # Quantifiable Metrics & Action Verbs
                st.markdown("#### 📈 Measurable Impact & Action Verbs")
                m_left, m_right = st.columns(2, gap='large')
                with m_left:
                    st.write("**Quantifiable Metrics Detected:**")
                    metrics = health.get('metrics_found', [])
                    if metrics:
                        st.write(", ".join(f"`{m}`" for m in metrics))
                    else:
                        st.warning("No measurable metrics detected! Add percentages, dollar savings, or scale numbers.")
                with m_right:
                    st.write("**Strong Action Verbs Used:**")
                    verbs = health.get('action_verbs_found', [])
                    if verbs:
                        st.write(", ".join(f"`{v}`" for v in verbs[:10]))
                    else:
                        st.info("No strong action verbs identified.")

                # Actionable Checklist
                st.markdown("#### 📋 Actionable ATS Health Checklist")
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

        with tabs[3]:
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

        with tabs[4]:
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

        with tabs[5]:
            st.subheader('ATS analysis')
            explanations = data.get('explanations', [])
            if explanations:
                for explanation in explanations:
                    st.write(f'- {explanation}')
            else:
                st.info('No additional explanations were returned.')


# ==============================================================================
# MODE 2: AUTO-JOB RECOMMENDER (FIND BEST MATCHING JOBS)
# ==============================================================================
elif main_nav == '🚀 Auto-Job Recommender (Find Best Matching Jobs)':
    st.subheader('🚀 Auto-Job Recommender')
    st.write(
        'Upload your resume, filter by role, experience level, and posted time, and let ResumeMatch ATS '
        'scan and rank the best matching jobs from Supabase.'
    )

    rec_resume = st.file_uploader(
        'Upload your resume to discover matching jobs',
        type=['pdf', 'docx', 'txt'],
        key='rec_resume_uploader',
        help='Supported formats: PDF, DOCX, and TXT.',
    )
    if rec_resume:
        st.session_state['saved_resume_tuple'] = (rec_resume.name, rec_resume.getvalue(), rec_resume.type)
        st.success(f'{rec_resume.name} loaded ({rec_resume.size / 1024:.0f} KB)')
    elif st.session_state.get('saved_resume_tuple'):
        st.info(f"Using resume uploaded earlier: **{st.session_state['saved_resume_tuple'][0]}**")

    with st.container(border=True):
        st.write('**Filter & Search Options**')
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

        st.divider()
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric('Jobs Scanned', f'{total_scanned}')
        m_col2.metric('Matches Found', f'{total_matched}')
        if recs:
            top_score = recs[0]['overall_score']
            m_col3.metric('Top ATS Match', f'{top_score:.1f}%')

        if not recs:
            st.info('No jobs met the selected experience or time criteria. Try selecting "All Experience Levels" or "All Time".')
        else:
            st.subheader(f'Top {len(recs)} Ranked Job Matches')
            for idx, r in enumerate(recs, start=1):
                score = r['overall_score']
                score_badge = '🟢' if score >= 75 else '🟡' if score >= 55 else '🔴'

                with st.container(border=True):
                    head_col1, head_col2 = st.columns([3, 1])
                    with head_col1:
                        st.markdown(f"### #{idx} {r['title']}")
                        desc_badge = '🟢 Full JD' if r.get('has_full_description') else '📋 Brief Summary'
                        st.markdown(f"🏢 **{r['company']}** | 📍 {r['location']} | 🕒 *{r.get('posted_label', 'Recent')}* | {desc_badge}")
                    with head_col2:
                        st.markdown(f"### {score_badge} {score:.1f}%")
                        st.caption(f"{r['recommendation']}")

                    st.write(
                        f"**Candidate Experience:** {r['candidate_experience']:.1f} yrs | "
                        f"**Required:** {r['required_experience']:.1f} yrs | "
                        f"**Gap:** {r['experience_gap']:.1f} yrs"
                    )

                    matched_skills_str = ', '.join(r.get('matched_skills', [])) or 'None identified'
                    missing_skills_str = ', '.join(r.get('missing_skills', [])) or 'None missing'
                    st.write(f"✅ **Matched Skills:** {matched_skills_str}")
                    st.write(f"⚠️ **Missing Skills:** {missing_skills_str}")

                    b_col1, b_col2 = st.columns([1, 2])
                    with b_col1:
                        if r.get('link'):
                            st.link_button('🔗 Apply / View Job Posting', r['link'], use_container_width=True)
                        else:
                            st.caption('No direct URL available')
                    with b_col2:
                        with st.expander('📄 View Job Description Preview'):
                            st.text(r.get('description', '')[:1200] + ('...' if len(r.get('description', '')) > 1200 else ''))

                    tailor_info = r.get('tailoring_suggestions')
                    if tailor_info and tailor_info.get('star_bullet_points'):
                        with st.expander('🎯 Tailored Resume Bullet Points for This Job', expanded=False):
                            st.caption(f"Role target: **{tailor_info.get('target_title', r['title'])}**")
                            for b in tailor_info.get('star_bullet_points', [])[:3]:
                                st.code(f"[{b.get('skill')}] {b.get('bullet_point')}", language='text')
