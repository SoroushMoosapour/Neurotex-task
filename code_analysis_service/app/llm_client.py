"""Client for the LLM Service."""

import logging
from typing import Dict, List

import httpx
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for the LLM Service."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        self.llm_service_url = settings.LLM_SERVICE_URL

        # Initialize the OpenAI client with a base URL pointing to our LLM Service
        self.client = AsyncOpenAI(
            base_url=f"{self.llm_service_url}/",
            api_key="dummy_key",  # Not used by our LLM Service
        )

        logger.info("Initialized LLM client with URL: %s", self.llm_service_url)

    async def analyze_function(self, function_code: str) -> List[str]:
        """
        Analyze a Python function and provide improvement suggestions.

        Args:
            function_code: The Python function code to analyze.

        Returns:
            A list of improvement suggestions.
        """
        try:
            # Call the LLM Service using the OpenAI client
            response = await self.client.chat.completions.create(
                model="dummy_model",  # Not used by our LLM Service
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Python code review assistant.",
                    },
                    {"role": "user", "content": function_code},
                ],
            )

            # Extract suggestions from the response
            return self._extract_suggestions(response)

        except Exception as e:
            logger.error("Error calling LLM Service: %s", str(e))

            # Fall back to direct HTTP request
            return await self._fallback_analyze_function(function_code)

    def _extract_suggestions(self, response: ChatCompletion) -> List[str]:
        """
        Extract suggestions from an OpenAI response.

        Args:
            response: The OpenAI response.

        Returns:
            A list of improvement suggestions.
        """
        content = response.choices[0].message.content
        if not content:
            return ["No suggestions available."]

        # Parse the response into a list of suggestions
        suggestions = []
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and (
                line.startswith("-") or line.startswith("*") or line[0].isdigit()
            ):
                suggestions.append(line.lstrip("- *1234567890. "))

        # If no suggestions were parsed, return the whole content
        if not suggestions:
            return [content]

        return suggestions

    async def _fallback_analyze_function(self, function_code: str) -> List[str]:
        """
        Analyze a Python function using a direct HTTP request to the LLM Service.

        Args:
            function_code: The Python function code to analyze.

        Returns:
            A list of improvement suggestions.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.llm_service_url}/analyze",
                    json={"function_code": function_code},
                    timeout=30.0,
                )

                response.raise_for_status()
                result = response.json()

                return result.get("suggestions", ["No suggestions available."])

        except Exception as e:
            logger.error("Error in fallback LLM Service call: %s", str(e))
            return [f"Error analyzing function: {str(e)}"]
