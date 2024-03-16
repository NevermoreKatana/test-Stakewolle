from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Base settings of project.
    """
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret_key: str
    debug: bool
    email_backend: str
    email_host: str
    email_port: int
    email_use_ssl: bool
    email_host_user: str
    email_host_password: str
    eh_api_key: str    
    model_config = SettingsConfigDict(env_file=".env")
    
@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()
