"""Main application module for the Local LLM Service."""

import logging
from typing import Dict, Any

from robyn import Robyn, jsonify
from robyn.robyn import Headers

from app.config import settings
from app.llm import LocalLLM
from app.models import GenerateRequest, GenerateResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the Robyn application
app = Robyn(__name__)

# Initialize the local LLM
llm = LocalLLM()


@app.post("/generate")
async def generate(request: Dict[str, Any], headers: Headers) -> Dict[str, Any]:
    """
    Generate text from a prompt.

    Args:
        request: The request body containing the prompt and generation parameters.
        headers: The request headers.

    Returns:
        A JSON response with the generated text or an error message.
    """
    try:
        # Parse the request
        generate_request = GenerateRequest(**request)

        # Generate text
        generated_text, tokens_generated = await llm.generate(
            prompt=generate_request.prompt,
            max_tokens=generate_request.max_tokens,
            temperature=generate_request.temperature,
            top_p=generate_request.top_p,
            top_k=generate_request.top_k,
            repetition_penalty=generate_request.repetition_penalty,
            stop_sequences=generate_request.stop_sequences,
        )

        # Return the response
        response = GenerateResponse(
            text=generated_text,
            tokens_generated=tokens_generated,
            model_name=llm.model_name,
        )
        return jsonify(response.model_dump())

    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        error_response = ErrorResponse(
            error="Failed to generate text",
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
    return jsonify(
        {
            "status": "ok",
            "service": settings.SERVICE_NAME,
            "model": llm.model_name,
        }
    )


if __name__ == "__main__":
    logger.info(
        "Starting %s on %s:%d with model %s",
        settings.SERVICE_NAME,
        settings.HOST,
        settings.PORT,
        llm.model_name,
    )
    app.start(host=settings.HOST, port=settings.PORT)
