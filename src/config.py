from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: str
    VALKEY_URL: str = "valkey://localhost:6379"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRATION_SECONDS: int = 900
    OTP_COOLDOWN_SECONDS: int = 60
    ENVIRONMENT: str = "development"

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1026
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str = "noreply@satzwerk.local"

    OPENAI_LLM_MODEL: str = "gpt-5-nano"
    LLM_TEMPERATURE: float = 1.0
    AI_MAX_ITERATIONS: int = 3


settings = Settings()  # pyright: ignore[reportCallIssue]
