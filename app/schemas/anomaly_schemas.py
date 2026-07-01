"""Anomaly detection-related Pydantic schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class AnomalyAlgorithm(str, Enum):
    """Anomaly detection algorithms."""
    ISOLATION_FOREST = "isolation_forest"
    STATISTICAL = "statistical"
    SPIKE = "spike"
    PATTERN = "pattern"


class AnomalyResponse(BaseModel):
    """Schema for anomaly response."""
    id: int
    log_id: int
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    detected_at: datetime
    model_version: str
    algorithm: str
    features_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    """Schema for anomaly list response."""
    total: int
    page: int
    page_size: int
    pages: int
    anomalies: List[AnomalyResponse]


class AnomalyFilterRequest(BaseModel):
    """Schema for filtering anomalies."""
    algorithm: Optional[AnomalyAlgorithm] = None
    is_anomaly: Optional[bool] = None
    min_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    max_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class AnomalyStatsResponse(BaseModel):
    """Schema for anomaly statistics."""
    total_logs: int
    total_anomalies: int
    anomaly_percentage: float
    algorithms_used: List[str]
    average_score: float
    max_score: float
    min_score: float
    most_recent_anomaly: Optional[datetime] = None
