"""Configuration settings for the Local LLM Service."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Local LLM Service."""

    # Service configuration
    SERVICE_NAME: str = "local-llm-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Model configuration
    MODEL_PATH: str = "./models/qwen-1.5b"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    TOP_K: int = 40
    REPETITION_PENALTY: float = 1.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
