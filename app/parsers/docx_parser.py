from docx import Document
from app.core.exceptions import InvalidResumeException
from .base_parser import BaseResumeParser
class DOCXResumeParser(BaseResumeParser):
    def parse(self,file_path):
        try:
            d=Document(str(file_path)); text='\n'.join(p.text.strip() for p in d.paragraphs if p.text.strip()).strip()
            if not text: raise InvalidResumeException('Could not extract text from DOCX resume.')
            return text
        except InvalidResumeException: raise
        except Exception as e: raise InvalidResumeException(f'Failed to parse DOCX resume: {e}') from e
