import logging
from datetime import datetime, timedelta, timezone
import requests
from app.core.config import settings

logger = logging.getLogger('app.services.supabase')


def format_relative_time(created_at_str: str) -> str:
    if not created_at_str:
        return 'Recently'
    try:
        dt = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 0:
            return 'Just now'
        if seconds < 3600:
            minutes = max(1, int(seconds // 60))
            return f'{minutes} min ago'
        if seconds < 86400:
            hours = int(seconds // 3600)
            return f'{hours} hr ago' if hours == 1 else f'{hours} hrs ago'
        if seconds < 86400 * 7:
            days = int(seconds // 86400)
            return f'{days} day ago' if days == 1 else f'{days} days ago'
        return dt.strftime('%b %d, %Y')
    except Exception:
        return 'Recently'


class SupabaseJobService:
    _cached_keywords: list[str] = None

    def __init__(self, url: str = None, key: str = None):
        self.url = (url or settings.supabase_url).rstrip('/')
        self.key = key or settings.supabase_key

    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    @property
    def headers(self) -> dict:
        return {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
        }

    def get_status(self) -> dict:
        if not self.is_configured():
            return {
                'configured': False,
                'connected': False,
                'message': 'Supabase URL or Key not set.'
            }
        try:
            res = requests.get(
                f'{self.url}/rest/v1/jobs?select=job_id&limit=1',
                headers={**self.headers, 'Prefer': 'count=exact'},
                timeout=5
            )
            if res.ok:
                total_range = res.headers.get('Content-Range', '')
                total = int(total_range.split('/')[-1]) if '/' in total_range else len(res.json())
                return {'configured': True, 'connected': True, 'job_count': total}
            return {
                'configured': True,
                'connected': False,
                'message': f'Supabase responded with status {res.status_code}'
            }
        except Exception as e:
            logger.warning('Failed to connect to Supabase: %s', e)
            return {'configured': True, 'connected': False, 'message': str(e)}

    def search_jobs(
        self,
        query: str = '',
        keyword: str = '',
        time_frame: str = 'all',
        limit: int = 40
    ) -> list[dict]:
        if not self.is_configured():
            return []
        try:
            params = {
                'select': 'job_id,title,company,city,state,country,min_experience_years,max_experience_years,skills,degree_required,full_description,search_keyword,created_at,collected_at,link',
                'limit': str(limit),
                'order': 'created_at.desc.nullslast'
            }

            if keyword and keyword.lower() != 'all':
                params['search_keyword'] = f'ilike.{keyword.strip()}'

            if query and query.strip():
                clean_q = query.strip().replace('*', '').replace('(', '').replace(')', '')
                params['or'] = f'(title.ilike.*{clean_q}*,company.ilike.*{clean_q}*,skills.ilike.*{clean_q}*,search_keyword.ilike.*{clean_q}*)'

            # Time posted filter (e.g. 24h, 3d, 7d, 30d)
            if time_frame and time_frame.lower() != 'all':
                now = datetime.now(timezone.utc)
                if time_frame in ('24h', '1d', 'day'):
                    cutoff = now - timedelta(hours=24)
                elif time_frame in ('3d', '3days'):
                    cutoff = now - timedelta(days=3)
                elif time_frame in ('7d', 'week'):
                    cutoff = now - timedelta(days=7)
                elif time_frame in ('30d', 'month'):
                    cutoff = now - timedelta(days=30)
                else:
                    cutoff = None

                if cutoff:
                    params['created_at'] = f'gte.{cutoff.isoformat()}'

            endpoint = f"{self.url}/rest/v1/jobs"
            res = requests.get(endpoint, headers=self.headers, params=params, timeout=8)
            if res.ok:
                jobs = res.json()
                return [self._format_job(j) for j in jobs]
            logger.warning('Supabase search returned %s: %s', res.status_code, res.text)
            return []
        except Exception as e:
            logger.error('Error querying Supabase jobs: %s', e)
            return []

    def get_job(self, job_id: str) -> dict | None:
        if not self.is_configured() or not job_id:
            return None
        try:
            endpoint = f"{self.url}/rest/v1/jobs"
            res = requests.get(
                endpoint,
                headers=self.headers,
                params={'job_id': f'eq.{job_id}', 'limit': '1'},
                timeout=8
            )
            if res.ok and res.json():
                return self._format_job(res.json()[0])
            return None
        except Exception as e:
            logger.error('Error fetching Supabase job %s: %s', job_id, e)
            return None

    def get_distinct_keywords(self) -> list[str]:
        if not self.is_configured():
            return []
        if SupabaseJobService._cached_keywords:
            return SupabaseJobService._cached_keywords

        try:
            all_kw = set()
            for offset in range(0, 6000, 1000):
                res = requests.get(
                    f"{self.url}/rest/v1/jobs",
                    headers=self.headers,
                    params={'select': 'search_keyword', 'offset': str(offset), 'limit': '1000'},
                    timeout=6
                )
                if res.ok:
                    rows = res.json()
                    if not rows:
                        break
                    for r in rows:
                        kw = r.get('search_keyword')
                        if kw and kw.strip():
                            all_kw.add(kw.strip())
                else:
                    break

            normalized = {}
            for kw in all_kw:
                norm = kw.title()
                norm = (
                    norm.replace('Aws', 'AWS')
                    .replace('Bi', 'BI')
                    .replace('Fastapi', 'FastAPI')
                    .replace('Ai', 'AI')
                    .replace('Devops', 'DevOps')
                )
                normalized[norm.lower()] = norm

            clean_list = sorted(normalized.values())
            SupabaseJobService._cached_keywords = clean_list
            return clean_list
        except Exception as e:
            logger.warning('Error fetching distinct keywords: %s', e)
            return []

    def _format_job(self, row: dict) -> dict:
        title = (row.get('title') or 'Unknown Title').strip()
        company = (row.get('company') or 'Unknown Company').strip()
        city = (row.get('city') or '').strip()
        state = (row.get('state') or '').strip()
        country = (row.get('country') or '').strip()
        location_parts = [p for p in [city, state, country] if p and p.lower() != 'not specified']
        location = ', '.join(location_parts) if location_parts else 'Location not specified'

        raw_desc = (row.get('full_description') or '').strip()
        has_rich_desc = bool(raw_desc and raw_desc.lower() != 'not specified' and len(raw_desc) > 50)

        min_exp = row.get('min_experience_years')
        max_exp = row.get('max_experience_years')
        skills = row.get('skills')
        degree = row.get('degree_required')
        created_at = row.get('created_at') or ''
        link = row.get('link') or ''

        if has_rich_desc:
            clean_desc = raw_desc
        else:
            sections = [f"Job Title: {title}", f"Company: {company}", f"Location: {location}"]
            if min_exp and str(min_exp).lower() != 'not specified':
                sections.append(f"Required Experience: {min_exp} years")
            if skills and str(skills).lower() != 'not specified':
                sections.append(f"Required Skills: {skills}")
            if degree and str(degree).lower() != 'not specified':
                sections.append(f"Required Degree: {degree}")
            clean_desc = "\n".join(sections)

        job_id = row.get('job_id') or ''
        short_id = job_id[-8:] if len(job_id) > 8 else job_id

        return {
            'job_id': job_id,
            'title': title,
            'company': company,
            'location': location,
            'min_experience_years': min_exp if str(min_exp).lower() != 'not specified' else None,
            'max_experience_years': max_exp if str(max_exp).lower() != 'not specified' else None,
            'skills': skills if str(skills).lower() != 'not specified' else None,
            'degree_required': degree if str(degree).lower() != 'not specified' else None,
            'has_full_description': has_rich_desc,
            'description': clean_desc,
            'search_keyword': row.get('search_keyword'),
            'created_at': created_at,
            'posted_label': format_relative_time(created_at),
            'link': link,
            'label': f"{title} @ {company} ({location}) [{short_id}]",
        }

