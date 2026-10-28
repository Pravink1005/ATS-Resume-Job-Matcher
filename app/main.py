import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.database import init_db
from app.api.routes_root import router as root_router
from app.api.routes_health import router as health_router
from app.api.routes_resume import router as resume_router
from app.api.routes_job import router as job_router
from app.api.routes_match import router as match_router
from app.api.routes_match_file import router as match_file_router
from app.api.routes_supabase import router as supabase_router

logger = logging.getLogger('app.main')
configure_logging()
init_db()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.exception_handler(Exception)
async def generic_error(request: Request, exc: Exception):
    logger.exception('Unhandled exception on %s %s: %s', request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={'detail': 'Internal server error'})

app.include_router(root_router)
app.include_router(health_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(match_router)
app.include_router(match_file_router)
app.include_router(supabase_router)
