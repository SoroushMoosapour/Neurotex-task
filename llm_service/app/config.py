"""Configuration settings for the LLM Service."""

from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Enum for supported LLM providers."""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class Settings(BaseSettings):
    """Settings for the LLM Service."""

    # Service configuration
    SERVICE_NAME: str = "llm-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"

    # LLM provider configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.LOCAL

    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # DeepSeek configuration
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-coder"

    # Anthropic configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # Local LLM configuration
    LOCAL_LLM_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
