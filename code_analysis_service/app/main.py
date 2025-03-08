"""Main application module for the Code Analysis Service."""

import logging
from typing import Dict, Any

from robyn import Robyn, jsonify
from robyn.robyn import Headers

from app.config import settings
from app.llm_client import LLMClient
from app.models import (
    AnalyzeStartRequest,
    AnalyzeStartResponse,
    AnalyzeFunctionRequest,
    AnalyzeFunctionResponse,
    ErrorResponse,
)
from app.repository import RepositoryManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the Robyn application
app = Robyn(__name__)

# Initialize the repository manager and LLM client
repo_manager = RepositoryManager()
llm_client = LLMClient()


@app.post("/analyze/start")
async def analyze_start(request: Dict[str, Any], headers: Headers) -> Dict[str, Any]:
    """
    Start a repository analysis job.

    Args:
        request: The request body containing the repository URL.
        headers: The request headers.

    Returns:
        A JSON response with the job ID or an error message.
    """
    try:
        # Parse the request
        analyze_request = AnalyzeStartRequest(**request)

        # Start the analysis
        job_id = await repo_manager.start_analysis(
            repo_url=analyze_request.repo_url,
            branch=analyze_request.branch,
        )

        # Return the response
        response = AnalyzeStartResponse(job_id=job_id)
        return jsonify(response.model_dump())

    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        error_response = ErrorResponse(
            error="Failed to start analysis",
            details=str(e),
        )
        return jsonify(error_response.model_dump(), status_code=500)


@app.post("/analyze/function")
async def analyze_function(request: Dict[str, Any], headers: Headers) -> Dict[str, Any]:
    """
    Analyze a function from a repository.

    Args:
        request: The request body containing the job ID and function name.
        headers: The request headers.

    Returns:
        A JSON response with suggestions or an error message.
    """
    try:
        # Parse the request
        analyze_request = AnalyzeFunctionRequest(**request)

        # Extract the function code
        function_code = await repo_manager.extract_function(
            job_id=analyze_request.job_id,
            function_name=analyze_request.function_name,
        )

        if not function_code:
            error_response = ErrorResponse(
                error="Function not found",
                details=f"Function {analyze_request.function_name} not found in repository",
            )
            return jsonify(error_response.model_dump(), status_code=404)

        # Analyze the function
        suggestions = await llm_client.analyze_function(function_code)

        # Return the response
        response = AnalyzeFunctionResponse(suggestions=suggestions)
        return jsonify(response.model_dump())

    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        error_response = ErrorResponse(
            error="Failed to analyze function",
            details=str(e),
        )
        return jsonify(error_response.model_dump(), status_code=500)


@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        A JSON response with the service status.
    """
    return jsonify({"status": "ok", "service": settings.SERVICE_NAME})


if __name__ == "__main__":
    logger.info(
        "Starting %s on %s:%d",
        settings.SERVICE_NAME,
        settings.HOST,
        settings.PORT,
    )
    app.start(host=settings.HOST, port=settings.PORT)
