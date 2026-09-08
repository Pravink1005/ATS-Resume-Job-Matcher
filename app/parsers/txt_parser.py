from pathlib import Path
from app.core.exceptions import InvalidResumeException
from .base_parser import BaseResumeParser
class TXTResumeParser(BaseResumeParser):
    def parse(self,file_path):
        try:
            text=Path(file_path).read_text(encoding='utf-8').strip()
            if not text: raise InvalidResumeException('Text resume is empty.')
            return text
        except UnicodeDecodeError as e: raise InvalidResumeException('Text resume must be UTF-8.') from e
