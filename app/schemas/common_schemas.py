"""Common reusable Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None


class MetadataSchema(BaseModel):
    """Metadata schema for logs."""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    total: int
    page: int
    page_size: int
    pages: int
    data: list


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int
