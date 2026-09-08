def match_keywords(required,candidate):
    r=set(required); c=set(candidate); m=sorted(r&c); miss=sorted(r-c); return {'score':round(100*len(m)/len(r),2) if r else 100.0,'matched':m,'missing':miss}
