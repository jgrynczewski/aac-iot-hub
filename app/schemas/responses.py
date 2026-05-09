"""
Response schemas for AAC IoT Hub API.

Standard response format for all API endpoints.
"""

from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    data: Any


class ErrorDetail(BaseModel):
    """Error details."""
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: ErrorDetail