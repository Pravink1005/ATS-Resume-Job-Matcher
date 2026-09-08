def match_experience(candidate,required,preferred=False):
    c=float(candidate or 0); r=float(required or 0)
    if r<=0:return {'score':100.0,'status':'No explicit experience requirement','gap':0.0}
    if c>=r:return {'score':100.0,'status':'Meets requirement','gap':0.0}
    ratio=c/r
    return {'score':round(max(0,min(100,ratio*100)),2),'status':f'{c:g} years vs {r:g} years required','gap':round(r-c,2)}
