"""Log-related Pydantic schemas."""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class LogLevel(str, Enum):
    """Log levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


class LogSource(str, Enum):
    """Log sources."""
    APPLICATION = "application"
    PLATFORM = "platform"
    API = "api"
    SYSTEM = "system"


class LogCreate(BaseModel):
    """Schema for creating a log entry."""
    timestamp: datetime
    level: LogLevel
    message: str = Field(..., min_length=1, max_length=2000)
    source: LogSource
    service: str = Field(..., min_length=1, max_length=255)
    metadata: Optional[Dict[str, Any]] = None
    file_source: Optional[str] = None
    raw_line: Optional[str] = None

    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace')
        return v


class LogResponse(BaseModel):
    """Schema for log response."""
    id: int
    timestamp: datetime
    level: str
    message: str
    source: str
    service: str
    metadata_json: Optional[Dict[str, Any]] = None
    file_source: Optional[str] = None

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """Schema for log list response."""
    total: int
    page: int
    page_size: int
    pages: int
    logs: List[LogResponse]


class LogFilterRequest(BaseModel):
    """Schema for filtering logs."""
    level: Optional[LogLevel] = None
    source: Optional[LogSource] = None
    service: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_term: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
