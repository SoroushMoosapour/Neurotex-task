"""Data models for the Local LLM Service."""

from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request model for text generation."""

    prompt: str = Field(..., description="The prompt to generate text from")
    max_tokens: int = Field(
        default=1000, description="Maximum number of tokens to generate"
    )
    temperature: float = Field(default=0.7, description="Sampling temperature")
    top_p: float = Field(default=0.9, description="Nucleus sampling parameter")
    top_k: int = Field(default=40, description="Top-k sampling parameter")
    repetition_penalty: float = Field(default=1.1, description="Repetition penalty")
    stop_sequences: Optional[List[str]] = Field(
        default=None, description="Sequences that stop generation"
    )


class GenerateResponse(BaseModel):
    """Response model for text generation."""

    text: str = Field(..., description="Generated text")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    model_name: str = Field(..., description="Name of the model used")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: str = Field(default="", description="Additional error details")
