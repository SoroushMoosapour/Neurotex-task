"""Tests for the configuration."""

import os
from unittest.mock import patch

from app.config import Settings


def test_settings_defaults():
    """Test the default settings."""
    # Create settings with default values
    settings = Settings()

    # Check the default values
    assert settings.SERVICE_NAME == "code-analysis-service"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8002
    assert settings.LOG_LEVEL == "INFO"
    assert settings.REPO_DIR == "./repos"
    assert settings.LLM_SERVICE_URL == "http://localhost:8001"


def test_settings_from_env():
    """Test loading settings from environment variables."""
    # Set environment variables
    with patch.dict(
        os.environ,
        {
            "SERVICE_NAME": "custom-service",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "REPO_DIR": "/custom/repos",
            "LLM_SERVICE_URL": "http://custom-llm-service:8001",
        },
    ):
        # Create settings
        settings = Settings()

        # Check the values
        assert settings.SERVICE_NAME == "custom-service"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 9000
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.REPO_DIR == "/custom/repos"
        assert settings.LLM_SERVICE_URL == "http://custom-llm-service:8001"
