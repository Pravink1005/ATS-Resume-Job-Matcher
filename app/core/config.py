from typing import Any
from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'Resume-to-Job Matching Engine'
    app_version: str = '2.0.0'
    debug: bool = False
    max_file_size_mb: int = 5
    database_url: str = 'sqlite:///./data/resume_matcher.db'
    cors_origins: str = 'http://127.0.0.1:8501,http://localhost:8501'
    supabase_url: str = Field(
        default='',
        validation_alias=AliasChoices('supabase_url', 'SUPABASE_URL', 'app_supabase_url')
    )
    supabase_key: str = Field(
        default='',
        validation_alias=AliasChoices(
            'supabase_key', 'SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE_KEY',
            'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY', 'app_supabase_key'
        )
    )
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='APP_',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on', 't')
        return bool(v)

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

settings = Settings()
