import re
DEGREES=['bachelor','b.sc','b.tech','b.e','bca','master','m.sc','m.tech','m.e','mca','mba','phd','diploma']
FIELDS=['computer science','statistics','mathematics','economics','information systems','information technology','data science','business analysis','business analytics']
def extract_education(text):
    low=text.lower(); return {'degrees':sorted({d for d in DEGREES if d in low}),'fields':sorted({f for f in FIELDS if f in low}),'has_bachelor':bool(re.search(r'\b(bachelor|b\.sc|b\.tech|b\.e|bca)\b',low)),'has_master':bool(re.search(r'\b(master|m\.sc|m\.tech|m\.e|mca|mba)\b',low))}
