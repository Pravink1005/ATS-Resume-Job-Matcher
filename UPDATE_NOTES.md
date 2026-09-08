# ResumeMatch ATS v3 — Accuracy Update

This update fixes the problems observed in the real UI test:

1. Resume experience no longer defaults to 0 when the resume uses date ranges such as `Jul 2025 - Present`.
2. The single-letter `R` skill is no longer detected from ordinary words containing the letter R. It is only detected when the resume explicitly says R programming/language/RStudio/using R.
3. Job parser uses the same safe R detection.
4. Keyword extraction is now ATS-concept based instead of returning noisy words such as `ability`, `across`, `bachelor`, `accuracy.` etc. as if all were equal keywords.
5. Skill partial matching is more conservative and avoids accidental matches.
6. Reporting/dashboard remain useful requirements, but are not allowed to inflate the score through loose substring matching.

The Streamlit UI remains:
- one resume only
- no configuration panel/sidebar
- explainable score breakdown

After replacing/updating the project, run:

```powershell
pytest -v
uvicorn app.main:app --reload
```

In another terminal:

```powershell
streamlit run frontend\app.py
```

If you already have an old SQLite database, keep it if you need old match history. The new matching logic is applied to new analyses. Existing stored matches are not automatically recalculated.


## Phase 1 — Evidence-Based ATS Scoring

Implemented before any UI redesign:
- Structured job requirement extraction (technical skills, responsibilities, competencies, education, experience).
- Required vs preferred detection for requirement sentences.
- Proficiency detection for basic/intermediate/advanced/expert wording.
- Conservative evidence matching against the resume.
- Related skills are supporting evidence only and do NOT count as direct skill matches.
- SQL no longer satisfies CTE/complex-join requirements automatically.
- Power BI no longer satisfies Tableau/Looker automatically.
- Requirement-level evidence is returned by the API for future explainable UI.
- Existing API/UI fields remain compatible.

The goal is accuracy, not score inflation. A missing requirement remains missing even when a nearby or related technology exists.
