"""Configuration settings for the Code Analysis Service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Code Analysis Service."""

    # Service configuration
    SERVICE_NAME: str = "code-analysis-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    LOG_LEVEL: str = "INFO"

    # Repository storage
    REPO_DIR: str = "./repos"

    # LLM Service configuration
    LLM_SERVICE_URL: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
