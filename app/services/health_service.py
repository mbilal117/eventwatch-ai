"""System health monitoring service."""

import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Log, Alert, Anomaly, SystemHealth
from app.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class HealthService:
    """Service for system health monitoring."""

    @staticmethod
    def calculate_health_score(db: Session) -> Dict[str, Any]:
        """Calculate current system health score."""
        try:
            total_logs = db.query(Log).count()
            error_count = db.query(Log).filter(Log.level.in_(['ERROR', 'CRITICAL'])).count()
            warning_count = db.query(Log).filter(Log.level == 'WARNING').count()
            anomaly_count = db.query(Anomaly).filter(Anomaly.is_anomaly == True).count()
            active_alerts = db.query(Alert).filter(Alert.resolved_at.is_(None)).count()

            error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0

            health_score = 100
            if total_logs > 0:
                health_score -= min(error_rate * 0.5, 30)
                health_score -= min((anomaly_count / total_logs * 100) * 0.3, 20)
                health_score -= min(active_alerts * 2, 20)

            health_score = max(0, min(100, health_score))

            health_data = {
                "health_score": health_score,
                "total_logs": total_logs,
                "error_count": error_count,
                "warning_count": warning_count,
                "anomaly_count": anomaly_count,
                "active_alerts": active_alerts,
                "error_rate": error_rate,
                "status": "healthy" if health_score >= 80 else "warning" if health_score >= 50 else "critical",
                "timestamp": datetime.utcnow().isoformat(),
            }

            HealthService._save_health_metric(db, health_data)
            return health_data

        except Exception as e:
            logger.error(f"Failed to calculate health score: {str(e)}")
            raise DatabaseException(f"Failed to calculate health score: {str(e)}")

    @staticmethod
    def _save_health_metric(db: Session, health_data: Dict[str, Any]) -> SystemHealth:
        """Save health metric to database."""
        try:
            metric = SystemHealth(
                health_score=health_data["health_score"],
                total_logs=health_data["total_logs"],
                error_count=health_data["error_count"],
                warning_count=health_data["warning_count"],
                anomaly_count=health_data["anomaly_count"],
                active_alerts=health_data["active_alerts"],
                error_rate=health_data["error_rate"],
                metadata_json={"status": health_data["status"]},
            )
            db.add(metric)
            db.commit()
            db.refresh(metric)
            return metric
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save health metric: {str(e)}")
            raise DatabaseException(f"Failed to save health metric: {str(e)}")

    @staticmethod
    def get_health_history(db: Session, hours: int = 24) -> list:
        """Get health history for the last N hours."""
        try:
            from sqlalchemy import desc
            from datetime import timedelta

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            metrics = db.query(SystemHealth).filter(
                SystemHealth.timestamp >= cutoff_time
            ).order_by(desc(SystemHealth.timestamp)).all()

            return [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "health_score": m.health_score,
                    "total_logs": m.total_logs,
                    "error_count": m.error_count,
                    "active_alerts": m.active_alerts,
                }
                for m in metrics
            ]
        except Exception as e:
            logger.error(f"Failed to get health history: {str(e)}")
            return []

    @staticmethod
    def get_health_status(db: Session) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            health_data = HealthService.calculate_health_score(db)
            history = HealthService.get_health_history(db, hours=24)

            return {
                "current": health_data,
                "history": history,
                "database_status": "connected",
            }
        except Exception as e:
            logger.error(f"Failed to get health status: {str(e)}")
            return {
                "current": {
                    "health_score": 0,
                    "status": "critical",
                    "error": str(e),
                },
                "database_status": "disconnected",
            }
