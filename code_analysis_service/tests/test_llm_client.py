"""Tests for the LLM client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.llm_client import LLMClient


@pytest.mark.asyncio
async def test_analyze_function_with_openai():
    """Test analyzing a function using the OpenAI client."""
    # Mock the OpenAI client
    with patch("app.llm_client.AsyncOpenAI") as mock_openai:
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

        # Create the client and call analyze_function
        client = LLMClient()
        result = await client.analyze_function("def add(a, b): return a + b")

        # Check the result
        assert result == ["Add type hints", "Add docstring", "Use f-strings"]

        # Check that the OpenAI client was called correctly
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert kwargs["model"] == "dummy_model"
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"
        assert "def add(a, b): return a + b" in kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_analyze_function_with_fallback():
    """Test analyzing a function using the fallback HTTP request."""
    # Mock the OpenAI client to raise an exception
    with patch("app.llm_client.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_chat = MagicMock()
        mock_client.chat = mock_chat

        mock_completions = MagicMock()
        mock_chat.completions = mock_completions

        mock_create = AsyncMock(side_effect=Exception("Failed to call OpenAI API"))
        mock_completions.create = mock_create

        # Mock the httpx client
        with patch("app.llm_client.httpx.AsyncClient") as mock_httpx:
            # Set up the mock response
            mock_client_instance = AsyncMock()
            mock_httpx.return_value.__aenter__.return_value = mock_client_instance

            mock_response = MagicMock()
            mock_client_instance.post.return_value = mock_response

            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                "suggestions": ["Add type hints", "Add docstring", "Use f-strings"]
            }

            # Create the client and call analyze_function
            client = LLMClient()
            result = await client.analyze_function("def add(a, b): return a + b")

            # Check the result
            assert result == ["Add type hints", "Add docstring", "Use f-strings"]

            # Check that the httpx client was called correctly
            mock_client_instance.post.assert_called_once()
            args, kwargs = mock_client_instance.post.call_args
            assert args[0] == f"{client.llm_service_url}/analyze"
            assert kwargs["json"]["function_code"] == "def add(a, b): return a + b"


@pytest.mark.asyncio
async def test_analyze_function_with_fallback_error():
    """Test analyzing a function with an error in the fallback HTTP request."""
    # Mock the OpenAI client to raise an exception
    with patch("app.llm_client.AsyncOpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_chat = MagicMock()
        mock_client.chat = mock_chat

        mock_completions = MagicMock()
        mock_chat.completions = mock_completions

        mock_create = AsyncMock(side_effect=Exception("Failed to call OpenAI API"))
        mock_completions.create = mock_create

        # Mock the httpx client to raise an exception
        with patch("app.llm_client.httpx.AsyncClient") as mock_httpx:
            mock_client_instance = AsyncMock()
            mock_httpx.return_value.__aenter__.return_value = mock_client_instance

            mock_client_instance.post.side_effect = Exception(
                "Failed to call LLM Service"
            )

            # Create the client and call analyze_function
            client = LLMClient()
            result = await client.analyze_function("def add(a, b): return a + b")

            # Check the result
            assert len(result) == 1
            assert "Error analyzing function" in result[0]
            assert "Failed to call LLM Service" in result[0]


def test_extract_suggestions():
    """Test extracting suggestions from an OpenAI response."""
    # Create a client
    client = LLMClient()

    # Create a mock response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_response.choices = [mock_choice]

    mock_message = MagicMock()
    mock_choice.message = mock_message

    # Test with a list of suggestions
    mock_message.content = "- Add type hints\n- Add docstring\n- Use f-strings"
    result = client._extract_suggestions(mock_response)
    assert result == ["Add type hints", "Add docstring", "Use f-strings"]

    # Test with a numbered list
    mock_message.content = "1. Add type hints\n2. Add docstring\n3. Use f-strings"
    result = client._extract_suggestions(mock_response)
    assert result == ["Add type hints", "Add docstring", "Use f-strings"]

    # Test with a mixed list
    mock_message.content = "- Add type hints\n* Add docstring\n1. Use f-strings"
    result = client._extract_suggestions(mock_response)
    assert result == ["Add type hints", "Add docstring", "Use f-strings"]

    # Test with no list markers
    mock_message.content = "You should add type hints, docstrings, and use f-strings."
    result = client._extract_suggestions(mock_response)
    assert result == ["You should add type hints, docstrings, and use f-strings."]

    # Test with empty content
    mock_message.content = ""
    result = client._extract_suggestions(mock_response)
    assert result == ["No suggestions available."]
