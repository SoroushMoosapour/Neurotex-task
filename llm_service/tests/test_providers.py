"""Tests for the LLM providers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.providers.openai_provider import OpenAIProvider
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.local_provider import LocalProvider


@pytest.mark.asyncio
async def test_openai_provider_analyze_function():
    """Test the OpenAI provider's analyze_function method."""
    # Mock the OpenAI client
    with patch("app.providers.openai_provider.AsyncOpenAI") as mock_openai:
        # Set up the mock response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_chat = MagicMock()
        mock_client.chat = mock_chat

        mock_completions = MagicMock()
        mock_chat.completions = mock_completions

        mock_create = AsyncMock()
        mock_completions.create = mock_create

        mock_response = MagicMock()
        mock_create.return_value = mock_response

        mock_choice = MagicMock()
        mock_response.choices = [mock_choice]

        mock_message = MagicMock()
        mock_choice.message = mock_message

        mock_message.content = "- Add type hints\n- Add docstring\n- Use f-strings"

        # Create the provider and call analyze_function
        provider = OpenAIProvider()
        result = await provider.analyze_function("def add(a, b): return a + b")

        # Check the result
        assert result == ["Add type hints", "Add docstring", "Use f-strings"]

        # Check that the OpenAI client was called correctly
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert kwargs["model"] == provider.model
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"
        assert "def add(a, b): return a + b" in kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_deepseek_provider_analyze_function():
    """Test the DeepSeek provider's analyze_function method."""
    # Mock the httpx client
    with patch("app.providers.deepseek_provider.httpx.AsyncClient") as mock_client:
        # Set up the mock response
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_client_instance.post.return_value = mock_response

        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "- Add type hints\n- Add docstring\n- Use f-strings"
                    }
                }
            ]
        }

        # Create the provider and call analyze_function
        provider = DeepSeekProvider()
        result = await provider.analyze_function("def add(a, b): return a + b")

        # Check the result
        assert result == ["Add type hints", "Add docstring", "Use f-strings"]

        # Check that the httpx client was called correctly
        mock_client_instance.post.assert_called_once()
        args, kwargs = mock_client_instance.post.call_args
        assert args[0] == provider.api_url
        assert "def add(a, b): return a + b" in kwargs["json"]["messages"][1]["content"]


@pytest.mark.asyncio
async def test_local_provider_analyze_function():
    """Test the Local provider's analyze_function method."""
    # Mock the httpx client
    with patch("app.providers.local_provider.httpx.AsyncClient") as mock_client:
        # Set up the mock response
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_client_instance.post.return_value = mock_response

        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "text": "- Add type hints\n- Add docstring\n- Use f-strings"
        }

        # Create the provider and call analyze_function
        provider = LocalProvider()
        result = await provider.analyze_function("def add(a, b): return a + b")

        # Check the result
        assert result == ["Add type hints", "Add docstring", "Use f-strings"]

        # Check that the httpx client was called correctly
        mock_client_instance.post.assert_called_once()
        args, kwargs = mock_client_instance.post.call_args
        assert args[0] == provider.api_url
        assert "def add(a, b): return a + b" in kwargs["json"]["prompt"]
