from pydantic_settings import BaseSettings
from pydantic import AnyUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


from functools import lru_cache
import uuid
import logging

class SecSettings(BaseSettings):
    # ── JWT ────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: SecretStr = SecretStr("change-me-in-production-please-use-256-bit")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ───────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        allowed = {"HS256", "HS384", "HS512", "RS256"}
        if v not in allowed:
            raise ValueError(f"JWT algorithm must be one of {allowed}")
        return v

class ProjectSettings(BaseSettings):
    PROJECT_TITLE: str = "kill-hand-service"
    PROJECT_DESCRIPTION: str =  """
    Сервис
    """
    BASE_PATH: str = "/notifications-service/"

class EmailSettings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_PASS: str
    SMTP_USER: str
    EMAIL_CHANNEL_ID: uuid.UUID
    EMAIL_FROM: str
    
    
class DataBaseSettings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    
    @property
    def database_url(self) -> str:
       return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" 

class LoggingSettings(BaseSettings):
    LOGGING_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s %(message)s"
    LOGGING_DATEFMT: str = "%Y-%m-d %H:%M:S"
    LOG_LEVEL: int = logging.INFO
    
    GRAYLOG_ENABLED: bool = False
    GRAYLOG_HOST: str | None = None
    GRAYLOG_PORT: int | None = None

class Settings(
    DataBaseSettings, 
    ProjectSettings, 
    EmailSettings,
    LoggingSettings,
    SecSettings
):
    ...
    
    
@lru_cache
def get_settings():
    return Settings()