"""Alert-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class AlertType(str, Enum):
    """Alert types."""
    SPIKE = "spike"
    PATTERN = "pattern"
    RATE_INCREASE = "rate_increase"
    ANOMALY = "anomaly"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Alert statuses."""
    CREATED = "created"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: int
    log_id: Optional[int] = None
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    webhook_sent: bool
    webhook_response: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for alert list response."""
    total: int
    page: int
    page_size: int
    pages: int
    alerts: List[AlertResponse]


class AlertFilterRequest(BaseModel):
    """Schema for filtering alerts."""
    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    resolved_only: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class AlertStatsResponse(BaseModel):
    """Schema for alert statistics."""
    total_alerts: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
    resolved_count: int
    active_count: int
    critical_alerts: int
    average_resolution_time_minutes: Optional[float] = None


class AlertHistoryResponse(BaseModel):
    """Schema for alert history."""
    id: int
    alert_id: int
    status: str
    changed_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
