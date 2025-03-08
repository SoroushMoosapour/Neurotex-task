"""Anthropic LLM provider implementation."""

import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider implementation."""

    def __init__(self) -> None:
        """Initialize the Anthropic provider."""
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self.api_url = "https://api.anthropic.com/v1/messages"
        logger.info("Initialized Anthropic provider with model: %s", self.model)

    async def analyze_function(self, function_code: str) -> List[str]:
        """
        Analyze a Python function using Anthropic Claude and provide improvement suggestions.

        Args:
            function_code: The Python function code to analyze.

        Returns:
            A list of improvement suggestions.
        """
        prompt = f"""
        Analyze the following Python function and provide a list of suggestions for improvement.
        Focus on code quality, readability, performance, and best practices.
        
        ```python
        {function_code}
        ```
        
        Provide your suggestions as a list of concise points.
        """

        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }

            payload: Dict[str, Any] = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1000,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )

                response.raise_for_status()
                result = response.json()

                # Extract suggestions from the response
                content = result.get("content", [{}])[0].get("text", "")
                if not content:
                    return ["No suggestions available."]

                # Parse the response into a list of suggestions
                suggestions = []
                for line in content.strip().split("\n"):
                    line = line.strip()
                    if line and (
                        line.startswith("-")
                        or line.startswith("*")
                        or line[0].isdigit()
                    ):
                        suggestions.append(line.lstrip("- *1234567890. "))

                # If no suggestions were parsed, return the whole content
                if not suggestions:
                    return [content]

                return suggestions

        except Exception as e:
            logger.error("Error calling Anthropic API: %s", str(e))
            return [f"Error analyzing function: {str(e)}"]
