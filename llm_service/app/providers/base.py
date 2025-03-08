"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import List


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def analyze_function(self, function_code: str) -> List[str]:
        """
        Analyze a Python function and provide improvement suggestions.

        Args:
            function_code: The Python function code to analyze.

        Returns:
            A list of improvement suggestions.
        """
        pass
