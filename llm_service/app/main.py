"""Main application module for the LLM Service."""

import logging
from typing import Dict, Any

from robyn import Robyn, jsonify
from robyn.robyn import Headers

from app.config import settings
from app.models import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from app.providers.factory import LLMProviderFactory

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the Robyn application
app = Robyn(__name__)

# Create the LLM provider
llm_provider = LLMProviderFactory.create_provider()


@app.post("/analyze")
async def analyze(request: Dict[str, Any], headers: Headers) -> Dict[str, Any]:
    """
    Analyze a Python function and provide improvement suggestions.

    Args:
        request: The request body containing the function code.
        headers: The request headers.

    Returns:
        A JSON response with suggestions or an error message.
    """
    try:
        # Parse the request
        analyze_request = AnalyzeRequest(**request)

        # Analyze the function
        suggestions = await llm_provider.analyze_function(analyze_request.function_code)

        # Return the response
        response = AnalyzeResponse(suggestions=suggestions)
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
        "Starting %s on %s:%d with provider %s",
        settings.SERVICE_NAME,
        settings.HOST,
        settings.PORT,
        settings.LLM_PROVIDER,
    )
    app.start(host=settings.HOST, port=settings.PORT)
