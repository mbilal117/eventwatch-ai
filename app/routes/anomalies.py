"""Anomaly detection routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.anomaly_service import AnomalyService
from app.schemas.anomaly_schemas import AnomalyResponse, AnomalyListResponse, AnomalyFilterRequest, AnomalyAlgorithm, AnomalyStatsResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("/", response_model=AnomalyListResponse)
async def get_anomalies(
    algorithm: Optional[AnomalyAlgorithm] = Query(None),
    is_anomaly: Optional[bool] = Query(None),
    min_score: Optional[float] = Query(0.0, ge=0.0, le=1.0),
    max_score: Optional[float] = Query(1.0, ge=0.0, le=1.0),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> AnomalyListResponse:
    """Get anomalies with filtering and pagination."""
    try:
        filters = AnomalyFilterRequest(
            algorithm=algorithm,
            is_anomaly=is_anomaly,
            min_score=min_score,
            max_score=max_score,
            page=page,
            page_size=page_size,
        )

        anomalies, total = AnomalyService.get_anomalies(db, filters)
        pages = (total + page_size - 1) // page_size

        return AnomalyListResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            anomalies=anomalies,
        )

    except Exception as e:
        logger.error(f"Get anomalies error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve anomalies: {str(e)}")


@router.get("/statistics/summary", response_model=AnomalyStatsResponse)
async def get_anomaly_statistics(db: Session = Depends(get_db)) -> AnomalyStatsResponse:
    """Get anomaly detection statistics."""
    try:
        stats = AnomalyService.get_anomaly_statistics(db)
        return AnomalyStatsResponse(
            total_logs=stats['total_logs'],
            total_anomalies=stats['total_anomalies'],
            anomaly_percentage=stats['anomaly_percentage'],
            algorithms_used=['isolation_forest', 'statistical', 'spike', 'pattern'],
            average_score=stats['average_score'],
            max_score=stats['max_score'],
            min_score=stats['min_score'],
        )

    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
