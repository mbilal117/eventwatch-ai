"""Alert management routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.alert_service import AlertService
from app.services.webhook_service import WebhookService
from app.schemas.alert_schemas import (
    AlertResponse, AlertListResponse, AlertFilterRequest,
    AlertType, AlertSeverity, AlertStatus, AlertStatsResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=AlertListResponse)
async def get_alerts(
    alert_type: Optional[AlertType] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    resolved_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
) -> AlertListResponse:
    """Get alerts with filtering and pagination."""
    try:
        filters = AlertFilterRequest(
            alert_type=alert_type,
            severity=severity,
            status=status,
            resolved_only=resolved_only,
            page=page,
            page_size=page_size,
        )

        alerts, total = AlertService.get_alerts(db, filters)
        pages = (total + page_size - 1) // page_size

        return AlertListResponse(
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            alerts=alerts,
        )

    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
) -> AlertResponse:
    """Get a specific alert by ID."""
    try:
        alert = AlertService.get_alert_by_id(db, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        return alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert: {str(e)}")


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    notes: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> AlertResponse:
    """Resolve an alert."""
    try:
        alert = AlertService.resolve_alert(db, alert_id, notes)
        return AlertResponse.model_validate(alert)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Resolve alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.put("/{alert_id}/escalate")
async def escalate_alert(
    alert_id: int,
    db: Session = Depends(get_db)
) -> AlertResponse:
    """Escalate an alert to higher severity."""
    try:
        alert = AlertService.escalate_alert(db, alert_id)
        return AlertResponse.model_validate(alert)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Escalate alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to escalate alert: {str(e)}")


@router.post("/{alert_id}/webhook")
async def send_alert_webhook(
    alert_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Manually send webhook notification for an alert."""
    try:
        alert = db.query(AlertService.__class__.__bases__[0].__subclasses__()[0]).filter(
            AlertService.__class__.__bases__[0].__subclasses__()[0].id == alert_id
        ).first()

        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

        success = WebhookService.send_webhook(alert)
        return {
            "success": success,
            "message": "Webhook" + (" sent" if success else " failed to send"),
            "alert_id": alert_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send webhook: {str(e)}")


@router.get("/statistics/summary", response_model=AlertStatsResponse)
async def get_alert_statistics(db: Session = Depends(get_db)) -> AlertStatsResponse:
    """Get alert statistics."""
    try:
        stats = AlertService.get_alert_statistics(db)
        return stats

    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
