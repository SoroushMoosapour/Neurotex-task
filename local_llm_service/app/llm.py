"""Local LLM implementation using Transformers."""

import logging
import os
from typing import List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.config import settings

logger = logging.getLogger(__name__)


class LocalLLM:
    """Local LLM implementation using Transformers."""

    _instance = None

    def __new__(cls):
        """Implement the Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(LocalLLM, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the local LLM."""
        if self._initialized:
            return

        logger.info("Initializing local LLM from %s", settings.MODEL_PATH)

        # Check if model path exists
        if not os.path.exists(settings.MODEL_PATH):
            logger.warning(
                "Model path %s does not exist. Using a small model for demonstration.",
                settings.MODEL_PATH,
            )
            # Use a small model for demonstration
            self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=True,
            )
        else:
            # Load the model from the specified path
            self.model_name = os.path.basename(settings.MODEL_PATH)
            self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_PATH)
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.MODEL_PATH,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=True,
            )

        logger.info("Local LLM initialized with model: %s", self.model_name)
        self._initialized = True

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repetition_penalty: float = 1.1,
        stop_sequences: Optional[List[str]] = None,
    ) -> tuple[str, int]:
        """
        Generate text from a prompt.

        Args:
            prompt: The prompt to generate text from.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            top_k: Top-k sampling parameter.
            repetition_penalty: Repetition penalty.
            stop_sequences: Sequences that stop generation.

        Returns:
            A tuple of (generated_text, tokens_generated).
        """
        logger.info(
            "Generating text with prompt: %s",
            prompt[:50] + "..." if len(prompt) > 50 else prompt,
        )

        # Encode the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        input_length = inputs.input_ids.shape[1]

        # Generate text
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode the generated text
        generated_text = self.tokenizer.decode(
            outputs[0][input_length:], skip_special_tokens=True
        )
        tokens_generated = outputs.shape[1] - input_length

        # Apply stop sequences
        if stop_sequences:
            for stop_seq in stop_sequences:
                if stop_seq in generated_text:
                    generated_text = generated_text[: generated_text.find(stop_seq)]

        logger.info("Generated %d tokens", tokens_generated)
        return generated_text, tokens_generated
