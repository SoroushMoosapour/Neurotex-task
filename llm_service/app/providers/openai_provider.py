"""OpenAI LLM provider implementation."""

import logging
from typing import List

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self) -> None:
        """Initialize the OpenAI provider."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        logger.info("Initialized OpenAI provider with model: %s", self.model)

    async def analyze_function(self, function_code: str) -> List[str]:
        """
        Analyze a Python function using OpenAI and provide improvement suggestions.

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
            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Python code review assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            # Extract suggestions from the response
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

        except Exception as e:
            logger.error("Error calling OpenAI API: %s", str(e))
            return [f"Error analyzing function: {str(e)}"]
