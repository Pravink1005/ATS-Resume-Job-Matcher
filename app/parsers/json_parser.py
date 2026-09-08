import json
from pathlib import Path
from app.core.exceptions import InvalidResumeException
from .base_parser import BaseResumeParser
class JSONResumeParser(BaseResumeParser):
    def parse(self,file_path):
        try:
            data=json.loads(Path(file_path).read_text(encoding='utf-8'))
            if not isinstance(data,dict): raise InvalidResumeException('JSON resume must be an object.')
            return json.dumps(data,ensure_ascii=False)
        except InvalidResumeException: raise
        except Exception as e: raise InvalidResumeException(f'Failed to parse JSON resume: {e}') from e
