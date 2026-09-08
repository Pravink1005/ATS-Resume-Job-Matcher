from pathlib import Path
from app.core.exceptions import UnsupportedFileTypeException
from .pdf_parser import PDFResumeParser
from .docx_parser import DOCXResumeParser
from .txt_parser import TXTResumeParser
from .json_parser import JSONResumeParser
class ResumeParserFactory:
    _PARSERS={'.pdf':PDFResumeParser,'.docx':DOCXResumeParser,'.txt':TXTResumeParser,'.json':JSONResumeParser}
    @classmethod
    def get_parser(cls,file_path):
        c=cls._PARSERS.get(Path(file_path).suffix.lower())
        if not c: raise UnsupportedFileTypeException(f'Unsupported resume format: {Path(file_path).suffix}')
        return c()
