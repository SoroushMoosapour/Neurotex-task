"""Factory for creating LLM providers."""

import logging
from typing import Dict, Type

from app.config import LLMProvider, settings
from app.providers.base import BaseLLMProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.deepseek_provider import DeepSeekProvider
from app.providers.local_provider import LocalProvider
from app.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers: Dict[LLMProvider, Type[BaseLLMProvider]] = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.DEEPSEEK: DeepSeekProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.LOCAL: LocalProvider,
    }

    @classmethod
    def create_provider(cls) -> BaseLLMProvider:
        """
        Create an LLM provider based on the configuration.

        Returns:
            An instance of the configured LLM provider.
        """
        provider_type = settings.LLM_PROVIDER
        provider_class = cls._providers.get(provider_type)

        if not provider_class:
            logger.error("Unsupported LLM provider: %s", provider_type)
            raise ValueError(f"Unsupported LLM provider: {provider_type}")

        logger.info("Creating LLM provider: %s", provider_type)
        return provider_class()
