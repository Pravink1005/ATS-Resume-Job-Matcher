from app.parsers.job_parser import JobDescriptionParser
class JobService:
    def parse(self,text): return JobDescriptionParser().parse(text)
