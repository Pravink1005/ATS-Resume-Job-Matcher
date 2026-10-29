import logging
from app.services.supabase_service import SupabaseJobService
from app.services.matching_service import MatchingService

logger = logging.getLogger('app.services.recommender')


def matches_experience_level(req_exp: float, level: str) -> bool:
    if not level or level.lower() in ('all', 'any'):
        return True
    if level == '0-2':
        return req_exp <= 2.0
    if level == '2-5':
        return 2.0 <= req_exp <= 5.0
    if level == '5+':
        return req_exp >= 5.0
    return True


class JobRecommenderService:
    def __init__(self):
        self.supabase = SupabaseJobService()
        self.matcher = MatchingService()

    def find_recommendations(
        self,
        resume_text: str,
        category: str = 'All',
        query: str = '',
        time_frame: str = 'all',
        experience_level: str = 'all',
        limit: int = 10,
        scan_limit: int = 35
    ) -> dict:
        if not self.supabase.is_configured():
            return {
                'recommendations': [],
                'total_scanned': 0,
                'total_matched': 0,
                'message': 'Supabase is not configured.'
            }

        if not resume_text or not resume_text.strip():
            return {
                'recommendations': [],
                'total_scanned': 0,
                'total_matched': 0,
                'message': 'Resume text is empty.'
            }

        # 1. Fetch live jobs from Supabase using category and time filters
        jobs = self.supabase.search_jobs(
            query=query,
            keyword=category,
            time_frame=time_frame,
            limit=scan_limit
        )

        if not jobs:
            return {
                'recommendations': [],
                'total_scanned': 0,
                'total_matched': 0,
                'message': 'No jobs found in Supabase matching these criteria.'
            }

        scored = []
        for job in jobs:
            try:
                match_res = self.matcher.match(resume_text, job['description'])
                req_exp = float(match_res.get('required_experience') or 0.0)

                # Check experience level filter (0-2, 2-5, 5+)
                if not matches_experience_level(req_exp, experience_level):
                    continue

                item = {
                    **match_res,
                    'job_id': job['job_id'],
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'link': job.get('link') or '',
                    'created_at': job.get('created_at') or '',
                    'posted_label': job.get('posted_label') or 'Recent',
                    'has_full_description': job.get('has_full_description', False),
                    'required_experience': req_exp,
                    'description': job['description'],
                }
                scored.append(item)
            except Exception as e:
                logger.warning('Failed to match job %s: %s', job.get('job_id'), e)
                continue

        # Sort recommendations from highest ATS score to lowest
        scored.sort(key=lambda x: x['overall_score'], reverse=True)

        return {
            'recommendations': scored[:limit],
            'total_scanned': len(jobs),
            'total_matched': len(scored),
            'category': category,
            'time_frame': time_frame,
            'experience_level': experience_level,
        }

