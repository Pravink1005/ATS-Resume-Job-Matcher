import time,logging
logger=logging.getLogger('resume_job_matcher.requests')
async def request_logging_middleware(request,call_next):
    start=time.perf_counter(); response=await call_next(request); logger.info('%s %s -> %s | %.3fs',request.method,request.url.path,response.status_code,time.perf_counter()-start); return response
