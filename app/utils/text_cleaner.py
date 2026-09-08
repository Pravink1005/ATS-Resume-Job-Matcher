import re
class TextCleaner:
    @staticmethod
    def normalize_newlines(text): return text.replace('\r\n','\n').replace('\r','\n')
    @staticmethod
    def normalize_whitespace(text): return re.sub(r'\s+', ' ', text).strip()
    @classmethod
    def clean(cls, text):
        if not isinstance(text, str): raise TypeError('Text must be a string.')
        if not text.strip(): return ''
        text=cls.normalize_newlines(text); text=cls.normalize_whitespace(text).lower()
        return re.sub(r"[^\w\s+#./-]", '', text).strip()
    @classmethod
    def clean_lines(cls,text):
        if not isinstance(text,str): raise TypeError('Text must be a string.')
        return [cls.clean(x) for x in cls.normalize_newlines(text).split('\n') if cls.clean(x)]
