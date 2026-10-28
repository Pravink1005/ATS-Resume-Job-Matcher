from pathlib import Path
from app.core.config import settings
from app.core.exceptions import InvalidResumeException, UnsupportedFileTypeException

class FileValidator:
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        if not isinstance(filename, str) or not filename.strip():
            raise InvalidResumeException('Filename cannot be empty.')
        ext = Path(filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeException(f'Unsupported file type: {ext}. Allowed: .pdf, .docx, .txt')
        return ext

    @classmethod
    def validate_size(cls, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise InvalidResumeException('File content must be bytes.')
        if not data:
            raise InvalidResumeException('Uploaded file is empty.')
        if len(data) > settings.max_file_size_mb * 1024 * 1024:
            raise InvalidResumeException(f'File exceeds {settings.max_file_size_mb} MB.')

    @classmethod
    def validate_magic_bytes(cls, ext: str, data: bytes) -> None:
        if ext == '.pdf':
            if not data.startswith(b'%PDF') and b'%PDF' not in data[:1024]:
                raise InvalidResumeException('File content does not match a valid PDF format.')
        elif ext == '.docx':
            if not data.startswith(b'PK\x03\x04'):
                raise InvalidResumeException('File content does not match a valid DOCX format.')

    @classmethod
    def validate(cls, filename: str, data: bytes, check_magic: bool = True) -> str:
        ext = cls.validate_filename(filename)
        cls.validate_size(data)
        if check_magic:
            cls.validate_magic_bytes(ext, data)
        return ext
