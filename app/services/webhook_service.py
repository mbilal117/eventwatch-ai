"""Webhook notification service."""

import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import Alert
from app.config import settings
from app.exceptions import WebhookException

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for webhook notifications."""

    @staticmethod
    def send_webhook(alert: Alert) -> bool:
        """Send webhook notification for an alert."""
        if not settings.webhook_url:
            logger.warning("Webhook URL not configured")
            return False

        severity_threshold = ["HIGH", "CRITICAL"]
        if alert.severity not in severity_threshold:
            logger.debug(f"Alert {alert.id} severity {alert.severity} below webhook threshold")
            return False

        try:
            payload = WebhookService._build_payload(alert)
            success = asyncio.run(WebhookService._send_async(payload))
            return success
        except Exception as e:
            logger.error(f"Failed to send webhook: {str(e)}")
            return False

    @staticmethod
    def _build_payload(alert: Alert) -> Dict[str, Any]:
        """Build webhook payload."""
        return {
            "alert_id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "log_id": alert.log_id,
            "metadata": alert.metadata_json or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def _send_async(payload: Dict[str, Any]) -> bool:
        """Send webhook asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=settings.webhook_timeout)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook sent successfully: {response.status}")
                        return True
                    else:
                        logger.warning(f"Webhook returned status {response.status}")
                        return False
        except asyncio.TimeoutError:
            logger.error("Webhook request timed out")
            return False
        except Exception as e:
            logger.error(f"Webhook request failed: {str(e)}")
            return False

    @staticmethod
    def update_webhook_status(db: Session, alert_id: int, success: bool, response: Optional[str] = None) -> Alert:
        """Update alert webhook status."""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.webhook_sent = success
                alert.webhook_response = response
                db.commit()
                db.refresh(alert)
            return alert
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update webhook status: {str(e)}")
            raise WebhookException(f"Failed to update webhook status: {str(e)}")

    @staticmethod
    def simulate_webhook(alert: Alert) -> str:
        """Simulate webhook notification (for testing)."""
        payload = WebhookService._build_payload(alert)
        logger.info(f"SIMULATED WEBHOOK:\n{payload}")
        return f"Webhook simulated for alert {alert.id}"
