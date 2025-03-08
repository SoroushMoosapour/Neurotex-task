"""Tests for the repository manager."""

import os
import pytest
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import HttpUrl

from app.models import JobStatus
from app.repository import RepositoryManager


@pytest.fixture
def repo_manager():
    """Create a repository manager with a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a repository manager with a temporary directory
        manager = RepositoryManager()
        manager.repo_dir = temp_dir
        manager.jobs_file = os.path.join(temp_dir, "jobs.json")

        # Create the repository directory
        os.makedirs(temp_dir, exist_ok=True)

        yield manager


@pytest.mark.asyncio
async def test_start_analysis(repo_manager):
    """Test starting a repository analysis job."""
    # Mock the _clone_repository method
    repo_manager._clone_repository = AsyncMock()

    # Start an analysis
    repo_url = HttpUrl("https://github.com/example/repo")
    job_id = await repo_manager.start_analysis(repo_url)

    # Check that a job was created
    assert job_id in repo_manager.jobs
    assert repo_manager.jobs[job_id].repo_url == repo_url
    assert repo_manager.jobs[job_id].status == "pending"

    # Check that _clone_repository was called
    repo_manager._clone_repository.assert_called_once_with(job_id, repo_url, "main")


@pytest.mark.asyncio
async def test_clone_repository_success(repo_manager):
    """Test cloning a repository successfully."""
    # Mock git.Repo.clone_from
    with patch("app.repository.git.Repo.clone_from") as mock_clone_from:
        # Create a job
        job_id = "test-job"
        repo_url = HttpUrl("https://github.com/example/repo")
        repo_path = os.path.join(repo_manager.repo_dir, job_id)

        job_status = JobStatus(
            job_id=job_id,
            status="pending",
            repo_url=repo_url,
            repo_path=repo_path,
            created_at="2023-01-01T00:00:00",
        )

        repo_manager.jobs[job_id] = job_status

        # Mock _save_jobs
        repo_manager._save_jobs = AsyncMock()

        # Clone the repository
        await repo_manager._clone_repository(job_id, repo_url, "main")

        # Check that git.Repo.clone_from was called
        mock_clone_from.assert_called_once_with(str(repo_url), repo_path, branch="main")

        # Check that the job status was updated
        assert repo_manager.jobs[job_id].status == "completed"
        assert repo_manager.jobs[job_id].completed_at is not None

        # Check that _save_jobs was called
        repo_manager._save_jobs.assert_called_once()


@pytest.mark.asyncio
async def test_clone_repository_failure(repo_manager):
    """Test cloning a repository with a failure."""
    # Mock git.Repo.clone_from to raise an exception
    with patch("app.repository.git.Repo.clone_from") as mock_clone_from:
        mock_clone_from.side_effect = Exception("Failed to clone repository")

        # Create a job
        job_id = "test-job"
        repo_url = HttpUrl("https://github.com/example/repo")
        repo_path = os.path.join(repo_manager.repo_dir, job_id)

        job_status = JobStatus(
            job_id=job_id,
            status="pending",
            repo_url=repo_url,
            repo_path=repo_path,
            created_at="2023-01-01T00:00:00",
        )

        repo_manager.jobs[job_id] = job_status

        # Mock _save_jobs
        repo_manager._save_jobs = AsyncMock()

        # Clone the repository
        await repo_manager._clone_repository(job_id, repo_url, "main")

        # Check that git.Repo.clone_from was called
        mock_clone_from.assert_called_once_with(str(repo_url), repo_path, branch="main")

        # Check that the job status was updated
        assert repo_manager.jobs[job_id].status == "failed"
        assert repo_manager.jobs[job_id].error == "Failed to clone repository"

        # Check that _save_jobs was called
        repo_manager._save_jobs.assert_called_once()


def test_get_job_status(repo_manager):
    """Test getting a job status."""
    # Create a job
    job_id = "test-job"
    repo_url = HttpUrl("https://github.com/example/repo")
    repo_path = os.path.join(repo_manager.repo_dir, job_id)

    job_status = JobStatus(
        job_id=job_id,
        status="completed",
        repo_url=repo_url,
        repo_path=repo_path,
        created_at="2023-01-01T00:00:00",
        completed_at="2023-01-01T00:01:00",
    )

    repo_manager.jobs[job_id] = job_status

    # Get the job status
    result = repo_manager.get_job_status(job_id)

    # Check the result
    assert result == job_status

    # Get a non-existent job status
    result = repo_manager.get_job_status("non-existent-job")

    # Check the result
    assert result is None


@pytest.mark.asyncio
async def test_extract_function(repo_manager):
    """Test extracting a function from a repository."""
    # Create a job
    job_id = "test-job"
    repo_url = HttpUrl("https://github.com/example/repo")
    repo_path = os.path.join(repo_manager.repo_dir, job_id)

    job_status = JobStatus(
        job_id=job_id,
        status="completed",
        repo_url=repo_url,
        repo_path=repo_path,
        created_at="2023-01-01T00:00:00",
        completed_at="2023-01-01T00:01:00",
    )

    repo_manager.jobs[job_id] = job_status

    # Mock _find_function
    repo_manager._find_function = AsyncMock(return_value="def test_function(): pass")

    # Extract a function
    result = await repo_manager.extract_function(job_id, "module.test_function")

    # Check the result
    assert result == "def test_function(): pass"

    # Check that _find_function was called
    repo_manager._find_function.assert_called_once_with(
        repo_path, "module", "test_function"
    )


@pytest.mark.asyncio
async def test_extract_function_job_not_found(repo_manager):
    """Test extracting a function from a non-existent job."""
    # Extract a function
    result = await repo_manager.extract_function(
        "non-existent-job", "module.test_function"
    )

    # Check the result
    assert result is None


@pytest.mark.asyncio
async def test_extract_function_job_not_completed(repo_manager):
    """Test extracting a function from a job that is not completed."""
    # Create a job
    job_id = "test-job"
    repo_url = HttpUrl("https://github.com/example/repo")
    repo_path = os.path.join(repo_manager.repo_dir, job_id)

    job_status = JobStatus(
        job_id=job_id,
        status="pending",
        repo_url=repo_url,
        repo_path=repo_path,
        created_at="2023-01-01T00:00:00",
    )

    repo_manager.jobs[job_id] = job_status

    # Extract a function
    result = await repo_manager.extract_function(job_id, "module.test_function")

    # Check the result
    assert result is None


def test_parse_function_name(repo_manager):
    """Test parsing a function name."""
    # Parse a function name with a module
    module_path, function_name = repo_manager._parse_function_name(
        "module.test_function"
    )

    # Check the result
    assert module_path == "module"
    assert function_name == "test_function"

    # Parse a function name with a nested module
    module_path, function_name = repo_manager._parse_function_name(
        "module.submodule.test_function"
    )

    # Check the result
    assert module_path == "module.submodule"
    assert function_name == "test_function"

    # Parse a function name without a module
    module_path, function_name = repo_manager._parse_function_name("test_function")

    # Check the result
    assert module_path == ""
    assert function_name == "test_function"


@pytest.mark.asyncio
async def test_find_function_with_module(repo_manager):
    """Test finding a function in a repository with a module path."""
    # Create a temporary file
    repo_path = repo_manager.repo_dir
    module_path = "module"
    function_name = "test_function"

    file_path = os.path.join(repo_path, module_path + ".py")

    # Create the file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Mock aiofiles.open
    mock_file = AsyncMock()
    mock_file.__aenter__.return_value.read = AsyncMock(
        return_value="def test_function():\n    pass\n"
    )

    with patch("app.repository.aiofiles.open", return_value=mock_file):
        with patch("app.repository.os.path.exists", return_value=True):
            # Find the function
            result = await repo_manager._find_function(
                repo_path, module_path, function_name
            )

            # Check the result
            assert result == "def test_function():\n    pass"


@pytest.mark.asyncio
async def test_find_function_without_module(repo_manager):
    """Test finding a function in a repository without a module path."""
    # Mock _search_function_in_repo
    repo_manager._search_function_in_repo = AsyncMock(
        return_value="def test_function(): pass"
    )

    # Find the function
    result = await repo_manager._find_function(
        repo_manager.repo_dir, "", "test_function"
    )

    # Check the result
    assert result == "def test_function(): pass"

    # Check that _search_function_in_repo was called
    repo_manager._search_function_in_repo.assert_called_once_with(
        repo_manager.repo_dir, "test_function"
    )


def test_extract_function_from_content(repo_manager):
    """Test extracting a function from file content."""
    # Extract a function
    content = "def test_function():\n    pass\n\ndef another_function():\n    pass\n"
    result = repo_manager._extract_function_from_content(content, "test_function")

    # Check the result
    assert result == "def test_function():\n    pass"

    # Extract a function with indentation
    content = "def test_function():\n    pass\n    # Comment\n\ndef another_function():\n    pass\n"
    result = repo_manager._extract_function_from_content(content, "test_function")

    # Check the result
    assert result == "def test_function():\n    pass\n    # Comment"

    # Extract a non-existent function
    result = repo_manager._extract_function_from_content(
        content, "non_existent_function"
    )

    # Check the result
    assert result is None
