ALIASES={'communication':{'presentation','stakeholder management','client communication'},'teamwork':{'collaboration','cross-functional'},'collaboration':{'teamwork','cross-functional'},'analytical thinking':{'critical thinking','problem solving'},'problem solving':{'critical thinking','analytical thinking'},'attention to detail':{'data quality','data validation'}}
def match_competencies(required,candidate):
    req=set(required); cand=set(candidate); matched=[]; missing=[]
    for r in req:
        if r in cand: matched.append(r)
        elif ALIASES.get(r,set()) & cand: matched.append(r)
        else: missing.append(r)
    score=100*len(matched)/len(req) if req else 100
    return {'score':round(score,2),'matched':sorted(matched),'missing':sorted(missing)}
