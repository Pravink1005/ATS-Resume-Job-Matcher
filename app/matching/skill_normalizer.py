ALIASES={'powerbi':'power bi','microsoft power bi':'power bi','microsoft excel':'excel','structured query language':'sql','postgres':'postgresql','postgres sql':'postgresql','python pandas':'pandas','numpy python':'numpy','exploratory data analysis':'eda','data cleansing':'data cleaning','data visualisation':'data visualization','data visualizations':'data visualization','key performance indicators':'kpi','business intelligence':'bi','tableau software':'tableau'}
def normalize_skill(s):
    s=' '.join(str(s).lower().strip().split()); return ALIASES.get(s,s)
def normalize_skills(items): return sorted({normalize_skill(x) for x in items if str(x).strip()})
