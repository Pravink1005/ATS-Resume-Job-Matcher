import os
import requests
import streamlit as st

API_URL=os.getenv('MATCHER_API_URL','http://127.0.0.1:8000')
st.set_page_config(page_title='ResumeMatch ATS',page_icon='📊',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
.block-container{max-width:1180px;padding-top:2rem}.hero{padding:1.2rem 0 1.8rem}.hero h1{font-size:2.6rem;margin:0}.hero p{font-size:1.1rem;opacity:.7}.score{font-size:4rem;font-weight:800;text-align:center}.muted{text-align:center;opacity:.7}.card{border:1px solid rgba(128,128,128,.25);border-radius:16px;padding:20px;height:100%}.pill{display:inline-block;padding:5px 10px;border-radius:999px;border:1px solid rgba(128,128,128,.25);margin:3px;font-size:.9rem}.good{font-weight:700;text-align:center;font-size:1.2rem}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>ResumeMatch ATS</h1><p>See how well one resume matches a job description — with explainable scoring.</p></div>',unsafe_allow_html=True)
col1,col2=st.columns(2,gap='large')
with col1:
    st.subheader('Your Resume')
    resume=st.file_uploader('Upload one resume',type=['pdf','docx','txt'],accept_multiple_files=False)
    if resume: st.success(f'✓ {resume.name}')
with col2:
    st.subheader('Job Description')
    jd=st.text_area('Paste the job description',height=250,placeholder='Paste the complete job description here...')

st.write('')
_,mid,_=st.columns([1,1,1])
with mid:
    analyze=st.button('Analyze Resume',type='primary',use_container_width=True)
if analyze:
    if not resume: st.error('Please upload a resume.'); st.stop()
    if not jd.strip(): st.error('Please paste a job description.'); st.stop()
    try:
        with st.spinner('Analyzing resume and matching requirements...'):
            resp=requests.post(f'{API_URL}/match/file',files={'resume_file':(resume.name,resume.getvalue(),resume.type)},data={'job_description':jd},timeout=90)
        if resp.status_code!=200: st.error(resp.json().get('detail','Matching failed.')); st.stop()
        data=resp.json(); st.session_state['result']=data
    except requests.RequestException as e: st.error(f'Could not connect to backend: {e}'); st.stop()

if 'result' in st.session_state:
    d=st.session_state['result']; st.divider(); st.subheader('ATS Match Score')
    st.markdown(f'<div class="score">{d["overall_score"]:.1f}%</div><div class="good">{d["recommendation"]}</div><div class="muted">Overall fit based on skills, experience, education, competencies, keywords and text similarity.</div>',unsafe_allow_html=True)
    st.progress(min(1,max(0,d['overall_score']/100)))
    st.divider(); st.subheader('Score Breakdown')
    scores=d['component_scores']; cols=st.columns(6)
    labels=[('Skills','skills'),('Experience','experience'),('Education','education'),('Competencies','competencies'),('Keywords','keywords'),('Similarity','tfidf')]
    for c,(label,key) in zip(cols,labels):
        c.metric(label,f'{scores[key]:.1f}%')
    st.divider(); a,b=st.columns(2)
    with a:
        st.subheader('Skills Analysis')
        st.markdown('**Matched**')
        st.write(', '.join(d['matched_skills']) if d['matched_skills'] else 'None')
        st.markdown('**Skills to Improve**')
        st.write(', '.join(d['missing_skills']) if d['missing_skills'] else 'None')
        st.caption(f'Exact: {len(d["exact_skill_matches"])} · Alias: {len(d["alias_skill_matches"])} · Partial: {len(d["partial_skill_matches"])} · Related: {len(d["related_skill_matches"])}')
    with b:
        st.subheader('Experience')
        st.write(f'**Your experience:** {d["candidate_experience"]:g} years')
        st.write(f'**Required:** {d["required_experience"]:g} years')
        st.write(f'**Gap:** {d["experience_gap"]:g} years')
        st.info(d['experience_status'])
    a,b=st.columns(2)
    with a:
        st.subheader('Education'); st.info(d['education_status'])
    with b:
        st.subheader('Professional Competencies'); st.write('**Matched:** '+(', '.join(d['matched_competencies']) if d['matched_competencies'] else 'None')); st.write('**Missing:** '+(', '.join(d['missing_competencies']) if d['missing_competencies'] else 'None'))
    st.divider(); a,b=st.columns(2)
    with a: st.subheader('Job Keywords'); st.write('**Matched:** '+(', '.join(d['matched_keywords']) if d['matched_keywords'] else 'None'))
    with b: st.write('**Missing:** '+(', '.join(d['missing_keywords']) if d['missing_keywords'] else 'None'))
    st.divider(); st.subheader('ATS Analysis')
    for x in d['explanations']: st.write('• '+x)
