from pathlib import Path
class BaseResumeParser:
    def parse(self,file_path:Path)->str: raise NotImplementedError
