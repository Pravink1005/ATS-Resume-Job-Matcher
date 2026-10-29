from app.core.exceptions import InvalidMatchTypeException, InvalidMatchValueException
from app.nlp.nlp_pipeline import NLPPipeline
from app.nlp.requirement_extractor import extract_requirements
from app.parsers.job_parser import JobDescriptionParser
from app.matching.skill_matcher import SkillMatcher
from app.matching.evidence_matcher import EvidenceMatcher
from app.matching.experience_intelligence import ExperienceIntelligence
from app.matching.education_intelligence import EducationIntelligence
from app.matching.competency_matcher import match_competencies
from app.matching.keyword_intelligence import KeywordIntelligence
from app.matching.tfidf_matcher import TFIDFMatcher
from app.matching.context_matcher import match_context
from app.scoring.scoring_engine import ScoringEngine
from app.services.ats_explanation_service import ATSExplanationService
from app.services.resume_health_service import ResumeHealthService
from app.services.resume_tailor_service import ResumeTailorService


class MatchingService:
    def __init__(self):
        self.nlp = NLPPipeline()
        self.job_parser = JobDescriptionParser()
        self.skill = SkillMatcher()
        self.evidence = EvidenceMatcher()
        self.exp = ExperienceIntelligence()
        self.edu = EducationIntelligence()
        self.kw = KeywordIntelligence()
        self.tfidf = TFIDFMatcher()
        self.scoring = ScoringEngine()
        self.explainer = ATSExplanationService()
        self.health_service = ResumeHealthService()
        self.tailor_service = ResumeTailorService()

    def extract_resume_data(self, text):
        if not isinstance(text, str):
            raise InvalidMatchTypeException('Resume text must be a string.')
        if not text.strip():
            return None
        return self.nlp.analyze(text)

    def extract_job_data(self, text):
        if not isinstance(text, str):
            raise InvalidMatchTypeException('Job description must be a string.')
        if not text.strip():
            return None
        return self.job_parser.parse(text)

    def parse_job_data(self, text):
        return self.extract_job_data(text)

    def match(self, resume_text, job_text):
        if not isinstance(resume_text, str) or not isinstance(job_text, str):
            raise InvalidMatchTypeException('Resume and job description must be strings.')
        if not resume_text.strip() or not job_text.strip():
            raise InvalidMatchValueException('Resume and job description cannot be empty.')

        rd = self.nlp.analyze(resume_text)
        jd = self.job_parser.parse(job_text)
        jd_nlp = self.nlp.analyze(job_text)
        context = match_context(resume_text, jd['job_title'], job_text)

        # Phase 1: extract explicit job requirements and match them to resume evidence.
        requirements = extract_requirements(job_text)
        requirement_analysis = self.evidence.match_requirements(requirements, resume_text, rd['skills'])

        sm = self.skill.match(jd['skills'], rd['skills'])
        # Experience remains transparent: a stated 2-year preference/requirement is
        # shown separately. The requirement extractor identifies whether it is preferred.
        exp_req = next((r for r in requirements if r['category'] == 'experience'), None)
        preferred_experience = bool(exp_req and not exp_req['required'])
        ex = self.exp.match(rd['experience'], jd['required_experience'], preferred=preferred_experience)
        ed = self.edu.match(rd['education'], jd['education'])

        # Fill the structured requirement records with the dedicated matcher results.
        for req in requirement_analysis:
            if req.get('category') == 'experience':
                req['status'] = 'matched' if ex['score'] >= 100 else 'partial'
                req['match_type'] = 'numeric_experience'
                req['score'] = ex['score']
                req['confidence'] = ex['score'] / 100.0
                req['evidence'] = (
                    f"Candidate: {rd['experience']:g} years; "
                    f"JD: {jd['required_experience']:g} years."
                )
                req['evidence_source'] = 'experience_matcher'
            elif req.get('category') == 'education':
                req['status'] = 'matched' if ed['score'] >= 100 else 'partial' if ed['score'] > 0 else 'missing'
                req['match_type'] = 'education_match'
                req['score'] = ed['score']
                req['confidence'] = ed['score'] / 100.0
                req['evidence'] = ed['status']
                req['evidence_source'] = 'education_matcher'

        cm = match_competencies(jd_nlp['competencies'], rd['competencies'])

        job_kw = [x for x in jd_nlp['keywords'] if x not in jd['skills']]
        resume_kw = rd['keywords']
        km = self.kw.match(job_kw, resume_kw)
        raw_sim, tfidf_calibrated = self.tfidf.calibrated_score(resume_text, job_text)

        # Skills are evidence-based: related skills are supporting evidence only.
        scores = {
            'skills': sm['score'],
            'experience': ex['score'],
            'education': ed['score'],
            'competencies': cm['score'],
            'keywords': km['score'],
            'tfidf': tfidf_calibrated,
            'title': context['title_match_score'] * .6 + context['seniority_score'] * .4,
            'context': (context['location_score'] + context['authorization_score']) / 2,
        }

        # Real ATS score: requirement-level evidence is the source of truth.
        # Dynamic weight redistribution ensures unstated categories do not unfairly penalize candidates.
        total, rec, weighted = self.scoring.calculate_ats(
            requirements=requirement_analysis,
            experience_score=ex['score'],
            education_score=ed['score'],
            tfidf_similarity=tfidf_calibrated,
            title_score=scores['title'],
            context_score=scores['context'],
            skills_score=scores['skills'],
        )

        result = {
            'overall_score': total,
            'recommendation': rec,
            'component_scores': {k: round(v, 2) for k, v in scores.items()},
            'weighted_scores': weighted,
            'matched_skills': sm['matched'],
            'missing_skills': sm['missing'],
            'exact_skill_matches': sm['exact'],
            'alias_skill_matches': sm['alias'],
            'partial_skill_matches': sm['partial'],
            'related_skill_matches': sm['related'],
            'matched_competencies': cm['matched'],
            'missing_competencies': cm['missing'],
            'matched_keywords': km['matched'],
            'missing_keywords': km['missing'],
            'experience_status': ex['status'],
            'candidate_experience': rd['experience'],
            'required_experience': jd['required_experience'],
            'experience_gap': ex['gap'],
            'education_status': ed['status'],
            'tfidf_similarity': raw_sim,
            'requirement_analysis': requirement_analysis,
            'ats_breakdown': weighted,
            'preferred_experience': preferred_experience,
            'job_title': jd['job_title'],
            'context_match': context,
        }
        result['explanations'] = self.explainer.explain(result)
        result['resume_health'] = self.health_service.audit(resume_text)
        result['tailoring_suggestions'] = self.tailor_service.generate_tailored_recommendations(
            resume_text=resume_text,
            job_description=job_text,
            match_result=result
        )
        return result
