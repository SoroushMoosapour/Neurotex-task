"""Data models for the LLM Service."""

from typing import List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request model for function analysis."""

    function_code: str = Field(..., description="Python function code to analyze")


class AnalyzeResponse(BaseModel):
    """Response model for function analysis."""

    suggestions: List[str] = Field(
        ..., description="List of suggestions for improving the function"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: str = Field(default="", description="Additional error details")
