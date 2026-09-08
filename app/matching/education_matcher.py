QUANT=['computer science','statistics','mathematics','economics','information systems','information technology','data science','business analysis','business analytics']
def match_education(resume,job):
    fields=set(resume.get('fields',[])); has_b=resume.get('has_bachelor',False); jobtxt=' '.join(job).lower()
    quantitative=any(f in fields for f in QUANT)
    if not job: return {'score':100.0,'status':'No explicit education requirement'}
    if has_b and quantitative:return {'score':100.0,'status':'Meets relevant bachelor/quantitative education requirement'}
    if has_b:return {'score':85.0,'status':'Bachelor degree found; field relevance should be reviewed'}
    return {'score':30.0,'status':'Required bachelor-level education not clearly found'}
