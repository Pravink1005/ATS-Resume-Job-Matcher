import re

# ATS concepts are deliberately curated instead of treating every English word as a keyword.
CONCEPTS = [
    'advanced sql','complex joins','ctes','query optimization','advanced excel','excel','python','pandas','numpy','r',
    'data extraction','data cleaning','data cleansing','data validation','data analysis','data analytics','trend analysis',
    'exploratory data analysis','eda','reporting','dashboard','dashboards','data visualization','power bi','tableau','looker',
    'kpi','key performance indicators','data governance','data quality','database','databases','sql queries','business insights',
    'actionable insights','decision making','decision-making','cross-functional','stakeholder','stakeholders','communication',
    'analytical','analytical thinking','accuracy','automation','automate','business intelligence'
]

STOP = {
    'the','and','for','with','that','this','from','into','are','will','you','your','our','their','have','has','years',
    'experience','required','preferred','using','work','working','role','job','description','ability','skills','responsibilities',
    'candidate','candidates','including','such','etc','must','should','can','may','who','what','how','about','across'
}


def extract_keywords(text, limit=40):
    low = text.lower()
    found = set()
    for concept in CONCEPTS:
        if concept == 'r':
            ok = bool(re.search(r'\br\s+(?:programming|language|studio)\b|\busing\s+r\b|\bprogramming\s+in\s+r\b', low))
        else:
            ok = bool(re.search(r'(?<!\w)' + re.escape(concept) + r'(?!\w)', low))
        if ok:
            found.add(concept)

    # Add useful non-stop single words only when repeated; this keeps the list explainable.
    words = re.findall(r'[a-zA-Z][a-zA-Z0-9+#.-]{2,}', low)
    freq = {}
    for word in words:
        if word not in STOP:
            freq[word] = freq.get(word, 0) + 1
    for word, count in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
        if count >= 2:
            found.add(word)
        if len(found) >= limit:
            break
    return sorted(found)[:limit]
