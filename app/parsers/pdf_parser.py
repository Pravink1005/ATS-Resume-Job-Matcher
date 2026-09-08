from pathlib import Path
from pypdf import PdfReader
from app.core.exceptions import InvalidResumeException
from .base_parser import BaseResumeParser
class PDFResumeParser(BaseResumeParser):
    def parse(self,file_path):
        try:
            reader=PdfReader(str(file_path)); text='\n'.join((p.extract_text() or '') for p in reader.pages).strip()
            if not text: raise InvalidResumeException('Could not extract text from PDF resume.')
            return text
        except InvalidResumeException: raise
        except Exception as e: raise InvalidResumeException(f'Failed to parse PDF resume: {e}') from e
