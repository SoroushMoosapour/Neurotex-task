"""Repository management module."""

import asyncio
import datetime
import json
import logging
import os
import re
import uuid
from typing import Dict, List, Optional, Tuple

import aiofiles
import git
from pydantic import HttpUrl

from app.config import settings
from app.models import JobStatus

logger = logging.getLogger(__name__)


class RepositoryManager:
    """Repository manager for cloning and analyzing repositories."""

    def __init__(self) -> None:
        """Initialize the repository manager."""
        self.repo_dir = settings.REPO_DIR
        self.jobs_file = os.path.join(self.repo_dir, "jobs.json")
        self.jobs: Dict[str, JobStatus] = {}
        self._load_jobs()

        # Create the repository directory if it doesn't exist
        os.makedirs(self.repo_dir, exist_ok=True)

    def _load_jobs(self) -> None:
        """Load jobs from the jobs file."""
        if not os.path.exists(self.jobs_file):
            return

        try:
            with open(self.jobs_file, "r") as f:
                jobs_data = json.load(f)

            for job_id, job_data in jobs_data.items():
                self.jobs[job_id] = JobStatus(**job_data)

            logger.info("Loaded %d jobs from %s", len(self.jobs), self.jobs_file)
        except Exception as e:
            logger.error("Error loading jobs: %s", str(e))

    async def _save_jobs(self) -> None:
        """Save jobs to the jobs file."""
        try:
            jobs_data = {job_id: job.model_dump() for job_id, job in self.jobs.items()}

            async with aiofiles.open(self.jobs_file, "w") as f:
                await f.write(json.dumps(jobs_data, indent=2))

            logger.info("Saved %d jobs to %s", len(self.jobs), self.jobs_file)
        except Exception as e:
            logger.error("Error saving jobs: %s", str(e))

    async def start_analysis(self, repo_url: HttpUrl, branch: str = "main") -> str:
        """
        Start a repository analysis job.

        Args:
            repo_url: URL of the GitHub repository to analyze.
            branch: Branch to analyze.

        Returns:
            The ID of the analysis job.
        """
        # Generate a job ID
        job_id = str(uuid.uuid4())

        # Create a job status
        repo_path = os.path.join(self.repo_dir, job_id)
        job_status = JobStatus(
            job_id=job_id,
            status="pending",
            repo_url=repo_url,
            repo_path=repo_path,
            created_at=datetime.datetime.now().isoformat(),
        )

        # Save the job status
        self.jobs[job_id] = job_status
        await self._save_jobs()

        # Start the repository cloning in the background
        asyncio.create_task(self._clone_repository(job_id, repo_url, branch))

        return job_id

    async def _clone_repository(
        self, job_id: str, repo_url: HttpUrl, branch: str
    ) -> None:
        """
        Clone a repository.

        Args:
            job_id: ID of the analysis job.
            repo_url: URL of the GitHub repository to clone.
            branch: Branch to clone.
        """
        job = self.jobs[job_id]

        try:
            logger.info("Cloning repository %s to %s", repo_url, job.repo_path)

            # Clone the repository
            git.Repo.clone_from(str(repo_url), job.repo_path, branch=branch)

            # Update the job status
            job.status = "completed"
            job.completed_at = datetime.datetime.now().isoformat()

            logger.info("Repository %s cloned successfully", repo_url)
        except Exception as e:
            logger.error("Error cloning repository %s: %s", repo_url, str(e))

            # Update the job status
            job.status = "failed"
            job.error = str(e)

        # Save the job status
        await self._save_jobs()

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Get the status of a job.

        Args:
            job_id: ID of the analysis job.

        Returns:
            The job status, or None if the job doesn't exist.
        """
        return self.jobs.get(job_id)

    async def extract_function(self, job_id: str, function_name: str) -> Optional[str]:
        """
        Extract a function from a repository.

        Args:
            job_id: ID of the analysis job.
            function_name: Name of the function to extract.

        Returns:
            The function code, or None if the function couldn't be found.
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error("Job %s not found", job_id)
            return None

        if job.status != "completed":
            logger.error("Job %s is not completed", job_id)
            return None

        # Parse the function name
        module_path, function_name = self._parse_function_name(function_name)

        # Find the function in the repository
        function_code = await self._find_function(
            job.repo_path, module_path, function_name
        )

        return function_code

    def _parse_function_name(self, function_name: str) -> Tuple[str, str]:
        """
        Parse a function name into a module path and function name.

        Args:
            function_name: Name of the function to parse.

        Returns:
            A tuple of (module_path, function_name).
        """
        parts = function_name.split(".")
        if len(parts) == 1:
            return "", parts[0]

        return ".".join(parts[:-1]), parts[-1]

    async def _find_function(
        self, repo_path: str, module_path: str, function_name: str
    ) -> Optional[str]:
        """
        Find a function in a repository.

        Args:
            repo_path: Path to the repository.
            module_path: Path to the module containing the function.
            function_name: Name of the function to find.

        Returns:
            The function code, or None if the function couldn't be found.
        """
        # Convert module path to file path
        if module_path:
            file_path = os.path.join(repo_path, module_path.replace(".", "/") + ".py")
        else:
            # If no module path is provided, search for the function in all Python files
            return await self._search_function_in_repo(repo_path, function_name)

        # Check if the file exists
        if not os.path.exists(file_path):
            logger.error("File %s not found", file_path)
            return None

        # Read the file
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()

        # Find the function in the file
        function_code = self._extract_function_from_content(content, function_name)

        return function_code

    async def _search_function_in_repo(
        self, repo_path: str, function_name: str
    ) -> Optional[str]:
        """
        Search for a function in all Python files in a repository.

        Args:
            repo_path: Path to the repository.
            function_name: Name of the function to find.

        Returns:
            The function code, or None if the function couldn't be found.
        """
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    # Read the file
                    async with aiofiles.open(file_path, "r") as f:
                        content = await f.read()

                    # Find the function in the file
                    function_code = self._extract_function_from_content(
                        content, function_name
                    )

                    if function_code:
                        return function_code

        logger.error("Function %s not found in repository", function_name)
        return None

    def _extract_function_from_content(
        self, content: str, function_name: str
    ) -> Optional[str]:
        """
        Extract a function from file content.

        Args:
            content: Content of the file.
            function_name: Name of the function to extract.

        Returns:
            The function code, or None if the function couldn't be found.
        """
        # Regular expression to match a function definition
        pattern = rf"def\s+{re.escape(function_name)}\s*\("

        # Find the function definition
        match = re.search(pattern, content)
        if not match:
            return None

        # Extract the function code
        start_pos = match.start()

        # Find the end of the function
        lines = content[start_pos:].split("\n")
        function_lines: List[str] = []

        # Add the function definition line
        function_lines.append(lines[0])

        # Find the indentation level of the function body
        if len(lines) > 1:
            indent_match = re.match(r"^(\s+)", lines[1])
            indent_level = len(indent_match.group(1)) if indent_match else 0

            # Add the function body lines
            for line in lines[1:]:
                if line.strip() == "" or line.startswith(" " * indent_level):
                    function_lines.append(line)
                else:
                    break

        return "\n".join(function_lines)
