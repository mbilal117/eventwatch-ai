"""System health monitoring routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.health_service import HealthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/")
async def get_health(db: Session = Depends(get_db)) -> dict:
    """Get system health status."""
    try:
        health_status = HealthService.get_health_status(db)
        return {
            "success": True,
            "data": health_status,
        }

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "success": False,
            "data": {
                "current": {
                    "health_score": 0,
                    "status": "critical",
                    "error": str(e),
                },
                "database_status": "disconnected",
            }
        }


@router.get("/score")
async def get_health_score(db: Session = Depends(get_db)) -> dict:
    """Get current health score."""
    try:
        health_data = HealthService.calculate_health_score(db)
        return {
            "success": True,
            "health_score": health_data["health_score"],
            "status": health_data["status"],
            "details": {
                "total_logs": health_data["total_logs"],
                "error_count": health_data["error_count"],
                "warning_count": health_data["warning_count"],
                "anomaly_count": health_data["anomaly_count"],
                "active_alerts": health_data["active_alerts"],
                "error_rate": health_data["error_rate"],
            }
        }

    except Exception as e:
        logger.error(f"Health score error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate health score: {str(e)}")


@router.get("/history")
async def get_health_history(
    hours: int = 24,
    db: Session = Depends(get_db)
) -> dict:
    """Get health history."""
    try:
        history = HealthService.get_health_history(db, hours)
        return {
            "success": True,
            "hours": hours,
            "history": history,
        }

    except Exception as e:
        logger.error(f"Health history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get health history: {str(e)}")
