from pathlib import Path
import re
class FilenameUtils:
    @staticmethod
    def sanitize(filename):
        if not isinstance(filename,str): raise TypeError('filename must be a string.')
        filename=filename.strip()
        if not filename:return 'resume'
        filename=Path(filename).name
        return re.sub(r'_+','_',re.sub(r'[^A-Za-z0-9._-]','_',filename))[:255]
