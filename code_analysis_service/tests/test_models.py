"""Tests for the models."""

import pytest
from pydantic import ValidationError

from app.models import (
    AnalyzeStartRequest,
    AnalyzeStartResponse,
    AnalyzeFunctionRequest,
    AnalyzeFunctionResponse,
    JobStatus,
    ErrorResponse,
)


def test_analyze_start_request():
    """Test the AnalyzeStartRequest model."""
    # Test with valid data
    request = AnalyzeStartRequest(
        repo_url="https://github.com/example/repo",
        branch="main",
    )
    assert request.repo_url == "https://github.com/example/repo"
    assert request.branch == "main"

    # Test with default branch
    request = AnalyzeStartRequest(
        repo_url="https://github.com/example/repo",
    )
    assert request.repo_url == "https://github.com/example/repo"
    assert request.branch == "main"

    # Test with invalid URL
    with pytest.raises(ValidationError):
        AnalyzeStartRequest(
            repo_url="not-a-url",
        )


def test_analyze_start_response():
    """Test the AnalyzeStartResponse model."""
    # Test with valid data
    response = AnalyzeStartResponse(
        job_id="test-job-id",
    )
    assert response.job_id == "test-job-id"
    assert response.status == "pending"

    # Test with custom status
    response = AnalyzeStartResponse(
        job_id="test-job-id",
        status="completed",
    )
    assert response.job_id == "test-job-id"
    assert response.status == "completed"


def test_analyze_function_request():
    """Test the AnalyzeFunctionRequest model."""
    # Test with valid data
    request = AnalyzeFunctionRequest(
        job_id="test-job-id",
        function_name="module.test_function",
    )
    assert request.job_id == "test-job-id"
    assert request.function_name == "module.test_function"

    # Test with missing job_id
    with pytest.raises(ValidationError):
        AnalyzeFunctionRequest(
            function_name="module.test_function",
        )

    # Test with missing function_name
    with pytest.raises(ValidationError):
        AnalyzeFunctionRequest(
            job_id="test-job-id",
        )


def test_analyze_function_response():
    """Test the AnalyzeFunctionResponse model."""
    # Test with valid data
    response = AnalyzeFunctionResponse(
        suggestions=["Add type hints", "Add docstring", "Use f-strings"],
    )
    assert response.suggestions == ["Add type hints", "Add docstring", "Use f-strings"]

    # Test with empty suggestions
    with pytest.raises(ValidationError):
        AnalyzeFunctionResponse(
            suggestions=[],
        )


def test_job_status():
    """Test the JobStatus model."""
    # Test with valid data
    job_status = JobStatus(
        job_id="test-job-id",
        status="pending",
        repo_url="https://github.com/example/repo",
        repo_path="/path/to/repo",
        created_at="2023-01-01T00:00:00",
    )
    assert job_status.job_id == "test-job-id"
    assert job_status.status == "pending"
    assert job_status.repo_url == "https://github.com/example/repo"
    assert job_status.repo_path == "/path/to/repo"
    assert job_status.created_at == "2023-01-01T00:00:00"
    assert job_status.completed_at is None
    assert job_status.error is None

    # Test with completed job
    job_status = JobStatus(
        job_id="test-job-id",
        status="completed",
        repo_url="https://github.com/example/repo",
        repo_path="/path/to/repo",
        created_at="2023-01-01T00:00:00",
        completed_at="2023-01-01T00:01:00",
    )
    assert job_status.job_id == "test-job-id"
    assert job_status.status == "completed"
    assert job_status.repo_url == "https://github.com/example/repo"
    assert job_status.repo_path == "/path/to/repo"
    assert job_status.created_at == "2023-01-01T00:00:00"
    assert job_status.completed_at == "2023-01-01T00:01:00"
    assert job_status.error is None

    # Test with failed job
    job_status = JobStatus(
        job_id="test-job-id",
        status="failed",
        repo_url="https://github.com/example/repo",
        repo_path="/path/to/repo",
        created_at="2023-01-01T00:00:00",
        error="Failed to clone repository",
    )
    assert job_status.job_id == "test-job-id"
    assert job_status.status == "failed"
    assert job_status.repo_url == "https://github.com/example/repo"
    assert job_status.repo_path == "/path/to/repo"
    assert job_status.created_at == "2023-01-01T00:00:00"
    assert job_status.completed_at is None
    assert job_status.error == "Failed to clone repository"


def test_error_response():
    """Test the ErrorResponse model."""
    # Test with valid data
    error_response = ErrorResponse(
        error="Failed to analyze function",
    )
    assert error_response.error == "Failed to analyze function"
    assert error_response.details == ""

    # Test with details
    error_response = ErrorResponse(
        error="Failed to analyze function",
        details="Function not found",
    )
    assert error_response.error == "Failed to analyze function"
    assert error_response.details == "Function not found"
