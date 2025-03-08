"""Data models for the Code Analysis Service."""

from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeStartRequest(BaseModel):
    """Request model for starting repository analysis."""

    repo_url: HttpUrl = Field(
        ..., description="URL of the GitHub repository to analyze"
    )
    branch: Optional[str] = Field(default="main", description="Branch to analyze")


class AnalyzeStartResponse(BaseModel):
    """Response model for starting repository analysis."""

    job_id: str = Field(..., description="ID of the analysis job")
    status: str = Field(default="pending", description="Status of the job")


class AnalyzeFunctionRequest(BaseModel):
    """Request model for analyzing a function."""

    job_id: str = Field(..., description="ID of the analysis job")
    function_name: str = Field(..., description="Name of the function to analyze")


class AnalyzeFunctionResponse(BaseModel):
    """Response model for function analysis."""

    suggestions: List[str] = Field(
        ..., description="List of suggestions for improving the function"
    )


class JobStatus(BaseModel):
    """Model for job status."""

    job_id: str = Field(..., description="ID of the analysis job")
    status: str = Field(..., description="Status of the job")
    repo_url: HttpUrl = Field(..., description="URL of the GitHub repository")
    repo_path: str = Field(..., description="Path to the cloned repository")
    created_at: str = Field(..., description="Time when the job was created")
    completed_at: Optional[str] = Field(
        default=None, description="Time when the job was completed"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if the job failed"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    details: str = Field(default="", description="Additional error details")
