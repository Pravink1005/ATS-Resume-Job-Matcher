import re
COMPETENCIES=['communication','teamwork','collaboration','problem solving','problem-solving','critical thinking','analytical thinking','attention to detail','decision making','presentation','stakeholder management','cross-functional','adaptability','leadership','time management']
def extract_competencies(text):
    low=text.lower(); return sorted({c for c in COMPETENCIES if c in low})
