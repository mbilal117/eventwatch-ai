"""Alert generation and management service."""

import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import Log, Alert, AlertHistory, Anomaly
from app.schemas.alert_schemas import AlertResponse, AlertFilterRequest, AlertStatsResponse
from app.exceptions import AlertException
from app.config import settings

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert generation and management."""

    @staticmethod
    def create_alert(
        db: Session,
        log_id: Optional[int],
        alert_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create an alert."""
        try:
            alert = Alert(
                log_id=log_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                metadata_json=metadata or {},
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)

            AlertService.create_alert_history(db, alert.id, "created")
            logger.info(f"Alert created: {alert.id} - {severity} - {alert_type}")
            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create alert: {str(e)}")
            raise AlertException(f"Failed to create alert: {str(e)}")

    @staticmethod
    def detect_and_create_alerts(db: Session, log_entry: Log) -> List[Alert]:
        """Detect anomalies and create alerts."""
        alerts = []

        try:
            anomaly = db.query(Anomaly).filter(Anomaly.log_id == log_entry.id).first()

            if log_entry.level in ['ERROR', 'CRITICAL']:
                alert = AlertService.create_alert(
                    db,
                    log_id=log_entry.id,
                    alert_type="spike",
                    severity="HIGH" if log_entry.level == "ERROR" else "CRITICAL",
                    message=f"{log_entry.level} detected in {log_entry.service}: {log_entry.message[:100]}",
                    metadata={
                        "level": log_entry.level,
                        "service": log_entry.service,
                        "source": log_entry.source
                    }
                )
                alerts.append(alert)

            if anomaly and anomaly.is_anomaly:
                alert = AlertService.create_alert(
                    db,
                    log_id=log_entry.id,
                    alert_type="anomaly",
                    severity="MEDIUM" if anomaly.anomaly_score < 0.8 else "HIGH",
                    message=f"Anomaly detected with score {anomaly.anomaly_score:.2f}",
                    metadata={
                        "anomaly_score": anomaly.anomaly_score,
                        "algorithm": anomaly.algorithm
                    }
                )
                alerts.append(alert)

            window_minutes = 5
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            similar_error_count = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.message == log_entry.message,
                Log.level == log_entry.level,
                Log.timestamp >= cutoff_time
            ).count()

            if similar_error_count > 3:
                alert = AlertService.create_alert(
                    db,
                    log_id=log_entry.id,
                    alert_type="pattern",
                    severity="MEDIUM",
                    message=f"Repeated error pattern detected: {similar_error_count} occurrences",
                    metadata={
                        "pattern_count": similar_error_count,
                        "time_window_minutes": window_minutes
                    }
                )
                alerts.append(alert)

            return alerts

        except Exception as e:
            logger.error(f"Failed to detect and create alerts: {str(e)}")
            return alerts

    @staticmethod
    def create_alert_history(db: Session, alert_id: int, status: str, notes: Optional[str] = None) -> AlertHistory:
        """Create alert history entry."""
        try:
            history = AlertHistory(
                alert_id=alert_id,
                status=status,
                notes=notes
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            return history
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create alert history: {str(e)}")
            raise AlertException(f"Failed to create alert history: {str(e)}")

    @staticmethod
    def resolve_alert(db: Session, alert_id: int, notes: Optional[str] = None) -> Alert:
        """Resolve an alert."""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException(f"Alert {alert_id} not found")

            alert.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)

            AlertService.create_alert_history(db, alert_id, "resolved", notes)
            logger.info(f"Alert {alert_id} resolved")
            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to resolve alert: {str(e)}")
            raise AlertException(f"Failed to resolve alert: {str(e)}")

    @staticmethod
    def escalate_alert(db: Session, alert_id: int) -> Alert:
        """Escalate an alert to higher severity."""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                raise AlertException(f"Alert {alert_id} not found")

            severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            current_idx = severity_order.index(alert.severity) if alert.severity in severity_order else 0

            if current_idx < len(severity_order) - 1:
                alert.severity = severity_order[current_idx + 1]
                db.commit()
                db.refresh(alert)

            AlertService.create_alert_history(db, alert_id, "escalated")
            logger.info(f"Alert {alert_id} escalated to {alert.severity}")
            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to escalate alert: {str(e)}")
            raise AlertException(f"Failed to escalate alert: {str(e)}")

    @staticmethod
    def get_alerts(db: Session, filters: AlertFilterRequest) -> Tuple[List[AlertResponse], int]:
        """Get alerts with filtering and pagination."""
        query = db.query(Alert)

        if filters.alert_type:
            query = query.filter(Alert.alert_type == filters.alert_type.value)
        if filters.severity:
            query = query.filter(Alert.severity == filters.severity.value)

        if filters.resolved_only:
            query = query.filter(Alert.resolved_at.isnot(None))
        else:
            if filters.status:
                if filters.status.value == "resolved":
                    query = query.filter(Alert.resolved_at.isnot(None))
                elif filters.status.value in ["created", "escalated", "acknowledged"]:
                    query = query.filter(Alert.resolved_at.is_(None))

        if filters.start_date:
            query = query.filter(Alert.triggered_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(Alert.triggered_at <= filters.end_date)

        total = query.count()
        offset = (filters.page - 1) * filters.page_size
        alerts = query.order_by(desc(Alert.triggered_at)).offset(offset).limit(filters.page_size).all()

        responses = [AlertResponse.model_validate(alert) for alert in alerts]
        return responses, total

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[AlertResponse]:
        """Get a single alert by ID."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        return AlertResponse.model_validate(alert) if alert else None

    @staticmethod
    def get_alert_statistics(db: Session) -> AlertStatsResponse:
        """Get alert statistics."""
        total_alerts = db.query(Alert).count()

        by_severity = {}
        for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            count = db.query(Alert).filter(Alert.severity == severity).count()
            by_severity[severity] = count

        by_type = {}
        for alert_type in ["spike", "pattern", "rate_increase", "anomaly"]:
            count = db.query(Alert).filter(Alert.alert_type == alert_type).count()
            by_type[alert_type] = count

        resolved_count = db.query(Alert).filter(Alert.resolved_at.isnot(None)).count()
        active_count = db.query(Alert).filter(Alert.resolved_at.is_(None)).count()
        critical_alerts = db.query(Alert).filter(Alert.severity == "CRITICAL", Alert.resolved_at.is_(None)).count()

        avg_resolution_time = None
        resolved_alerts = db.query(Alert).filter(Alert.resolved_at.isnot(None)).all()
        if resolved_alerts:
            times = [(alert.resolved_at - alert.triggered_at).total_seconds() for alert in resolved_alerts]
            avg_resolution_time = sum(times) / len(times) / 60

        return AlertStatsResponse(
            total_alerts=total_alerts,
            by_severity=by_severity,
            by_type=by_type,
            resolved_count=resolved_count,
            active_count=active_count,
            critical_alerts=critical_alerts,
            average_resolution_time_minutes=avg_resolution_time,
        )

    @staticmethod
    def cleanup_old_alerts(db: Session, days: int = 30) -> int:
        """Delete old alerts."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = db.query(Alert).filter(
                Alert.resolved_at.isnot(None),
                Alert.resolved_at < cutoff_date
            )
            count = query.delete()
            db.commit()
            logger.info(f"Deleted {count} old alerts")
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to clean up old alerts: {str(e)}")
            raise AlertException(f"Failed to clean up old alerts: {str(e)}")
