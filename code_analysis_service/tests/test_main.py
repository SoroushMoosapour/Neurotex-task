"""Tests for the main application."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from robyn import Robyn
from robyn.robyn import Headers

from app.main import analyze_start, analyze_function, health


@pytest.mark.asyncio
async def test_analyze_start():
    """Test the analyze_start endpoint."""
    # Mock the repository manager
    with patch("app.main.repo_manager") as mock_repo_manager:
        # Set up the mock response
        mock_repo_manager.start_analysis = AsyncMock(return_value="test-job-id")

        # Call the endpoint
        request = {
            "repo_url": "https://github.com/example/repo",
            "branch": "main",
        }
        headers = Headers({})

        response = await analyze_start(request, headers)

        # Check the response
        assert isinstance(response, dict)
        assert response["job_id"] == "test-job-id"
        assert response["status"] == "pending"

        # Check that start_analysis was called
        mock_repo_manager.start_analysis.assert_called_once_with(
            repo_url=request["repo_url"],
            branch=request["branch"],
        )


@pytest.mark.asyncio
async def test_analyze_start_error():
    """Test the analyze_start endpoint with an error."""
    # Mock the repository manager
    with patch("app.main.repo_manager") as mock_repo_manager:
        # Set up the mock response
        mock_repo_manager.start_analysis = AsyncMock(
            side_effect=Exception("Failed to start analysis")
        )

        # Call the endpoint
        request = {
            "repo_url": "https://github.com/example/repo",
            "branch": "main",
        }
        headers = Headers({})

        response = await analyze_start(request, headers)

        # Check the response
        assert isinstance(response, dict)
        assert response["error"] == "Failed to start analysis"
        assert "Failed to start analysis" in response["details"]


@pytest.mark.asyncio
async def test_analyze_function():
    """Test the analyze_function endpoint."""
    # Mock the repository manager and LLM client
    with patch("app.main.repo_manager") as mock_repo_manager:
        with patch("app.main.llm_client") as mock_llm_client:
            # Set up the mock responses
            mock_repo_manager.extract_function = AsyncMock(
                return_value="def test_function(): pass"
            )
            mock_llm_client.analyze_function = AsyncMock(
                return_value=["Add type hints", "Add docstring", "Use f-strings"]
            )

            # Call the endpoint
            request = {
                "job_id": "test-job-id",
                "function_name": "module.test_function",
            }
            headers = Headers({})

            response = await analyze_function(request, headers)

            # Check the response
            assert isinstance(response, dict)
            assert response["suggestions"] == [
                "Add type hints",
                "Add docstring",
                "Use f-strings",
            ]

            # Check that extract_function and analyze_function were called
            mock_repo_manager.extract_function.assert_called_once_with(
                job_id=request["job_id"],
                function_name=request["function_name"],
            )
            mock_llm_client.analyze_function.assert_called_once_with(
                "def test_function(): pass"
            )


@pytest.mark.asyncio
async def test_analyze_function_not_found():
    """Test the analyze_function endpoint with a function not found."""
    # Mock the repository manager
    with patch("app.main.repo_manager") as mock_repo_manager:
        # Set up the mock response
        mock_repo_manager.extract_function = AsyncMock(return_value=None)

        # Call the endpoint
        request = {
            "job_id": "test-job-id",
            "function_name": "module.test_function",
        }
        headers = Headers({})

        response = await analyze_function(request, headers)

        # Check the response
        assert isinstance(response, dict)
        assert response["error"] == "Function not found"
        assert "not found in repository" in response["details"]


@pytest.mark.asyncio
async def test_analyze_function_error():
    """Test the analyze_function endpoint with an error."""
    # Mock the repository manager
    with patch("app.main.repo_manager") as mock_repo_manager:
        # Set up the mock response
        mock_repo_manager.extract_function = AsyncMock(
            side_effect=Exception("Failed to extract function")
        )

        # Call the endpoint
        request = {
            "job_id": "test-job-id",
            "function_name": "module.test_function",
        }
        headers = Headers({})

        response = await analyze_function(request, headers)

        # Check the response
        assert isinstance(response, dict)
        assert response["error"] == "Failed to analyze function"
        assert "Failed to extract function" in response["details"]


@pytest.mark.asyncio
async def test_health():
    """Test the health endpoint."""
    # Call the endpoint
    response = await health()

    # Check the response
    assert isinstance(response, dict)
    assert response["status"] == "ok"
    assert "code-analysis-service" in response["service"]
