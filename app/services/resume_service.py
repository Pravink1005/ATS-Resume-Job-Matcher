from pathlib import Path
import tempfile
from app.core.exceptions import InvalidResumeException
from app.parsers import ResumeParserFactory
from app.utils.file_validator import FileValidator
class ResumeService:
    def extract_text(self,file_path): return ResumeParserFactory.get_parser(Path(file_path)).parse(Path(file_path))
    def extract_text_from_file(self,file_content,filename):
        ext=FileValidator.validate(filename,file_content)
        with tempfile.NamedTemporaryFile(delete=False,suffix=ext) as f: f.write(file_content); path=Path(f.name)
        try:
            text=ResumeParserFactory.get_parser(path).parse(path)
            if not text.strip(): raise InvalidResumeException('Resume contains no readable text.')
            return text
        finally:path.unlink(missing_ok=True)
