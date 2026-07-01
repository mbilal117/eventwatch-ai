"""Anomaly detection service."""

import logging
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from sklearn.ensemble import IsolationForest

from app.database.models import Log, Anomaly
from app.schemas.anomaly_schemas import AnomalyResponse, AnomalyFilterRequest
from app.exceptions import AnomalyDetectionException
from app.config import settings

logger = logging.getLogger(__name__)


class AnomalyService:
    """Service for anomaly detection."""

    _isolation_forest_model: Optional[IsolationForest] = None
    _model_training_count: int = 0

    @staticmethod
    def detect_statistical_anomaly(db: Session, log_id: int, log_entry: Log) -> float:
        """Detect anomalies using statistical methods."""
        try:
            window_hours = 1
            cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)

            similar_logs = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.level == log_entry.level,
                Log.timestamp >= cutoff_time
            ).count()

            same_message_count = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.message == log_entry.message,
                Log.timestamp >= cutoff_time
            ).count()

            if similar_logs == 0:
                return 0.0

            repetition_ratio = same_message_count / similar_logs
            return min(1.0, repetition_ratio * 0.5)

        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {str(e)}")
            return 0.0

    @staticmethod
    def detect_spike_anomaly(db: Session, log_id: int, log_entry: Log) -> float:
        """Detect error spikes."""
        try:
            window_minutes = 5
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

            current_period_count = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.level.in_(['ERROR', 'CRITICAL']),
                Log.timestamp >= cutoff_time
            ).count()

            previous_period_count = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.level.in_(['ERROR', 'CRITICAL']),
                Log.timestamp >= cutoff_time - timedelta(minutes=window_minutes),
                Log.timestamp < cutoff_time
            ).count()

            if previous_period_count == 0 and current_period_count > 0:
                return 0.8

            if previous_period_count > 0:
                ratio = current_period_count / previous_period_count
                if ratio > 1.5:
                    return min(1.0, (ratio - 1.5) * 0.5)

            return 0.0

        except Exception as e:
            logger.error(f"Spike anomaly detection failed: {str(e)}")
            return 0.0

    @staticmethod
    def detect_pattern_anomaly(db: Session, log_id: int, log_entry: Log) -> float:
        """Detect repeated error patterns."""
        try:
            window_minutes = 5
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

            message_pattern_count = db.query(Log).filter(
                Log.service == log_entry.service,
                Log.level == log_entry.level,
                Log.message.like(f"%{log_entry.message[:50]}%"),
                Log.timestamp >= cutoff_time
            ).count()

            if message_pattern_count > 3:
                return min(1.0, (message_pattern_count - 3) * 0.1)

            return 0.0

        except Exception as e:
            logger.error(f"Pattern anomaly detection failed: {str(e)}")
            return 0.0

    @staticmethod
    def detect_isolation_forest_anomaly(db: Session, log_id: int) -> float:
        """Detect anomalies using Isolation Forest."""
        try:
            AnomalyService._train_model_if_needed(db)

            if AnomalyService._isolation_forest_model is None:
                return 0.0

            features = AnomalyService._extract_features(db, log_id)
            if features is None:
                return 0.0

            X = np.array([features])
            anomaly_score = AnomalyService._isolation_forest_model.score_samples(X)[0]
            normalized_score = 1.0 / (1.0 + np.exp(-anomaly_score))

            return float(min(1.0, max(0.0, normalized_score)))

        except Exception as e:
            logger.error(f"Isolation Forest anomaly detection failed: {str(e)}")
            return 0.0

    @staticmethod
    def _extract_features(db: Session, log_id: int) -> Optional[Tuple]:
        """Extract features from log for ML model."""
        try:
            window_minutes = 60
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)

            log = db.query(Log).filter(Log.id == log_id).first()
            if not log:
                return None

            service_error_count = db.query(Log).filter(
                Log.service == log.service,
                Log.level.in_(['ERROR', 'CRITICAL']),
                Log.timestamp >= cutoff_time
            ).count()

            service_warning_count = db.query(Log).filter(
                Log.service == log.service,
                Log.level == 'WARNING',
                Log.timestamp >= cutoff_time
            ).count()

            message_length = len(log.message)
            level_encoding = {'INFO': 0, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 3}.get(log.level, 0)

            return (service_error_count, service_warning_count, message_length, level_encoding)

        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return None

    @staticmethod
    def _train_model_if_needed(db: Session) -> None:
        """Train Isolation Forest model if needed."""
        try:
            total_logs = db.query(Log).count()

            if AnomalyService._model_training_count == 0 or total_logs - AnomalyService._model_training_count > 100:
                AnomalyService._train_model(db)

        except Exception as e:
            logger.error(f"Model training check failed: {str(e)}")

    @staticmethod
    def _train_model(db: Session) -> None:
        """Train the Isolation Forest model."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            logs = db.query(Log).filter(Log.timestamp >= cutoff_time).all()

            if len(logs) < 10:
                logger.warning("Insufficient logs for training (need at least 10)")
                return

            features = []
            for log in logs:
                feature_tuple = AnomalyService._extract_features(db, log.id)
                if feature_tuple:
                    features.append(feature_tuple)

            if not features:
                return

            X = np.array(features)
            AnomalyService._isolation_forest_model = IsolationForest(
                contamination=settings.isolation_forest_contamination,
                random_state=42,
                n_estimators=100
            )
            AnomalyService._isolation_forest_model.fit(X)
            AnomalyService._model_training_count = len(logs)

            logger.info(f"Isolation Forest model trained with {len(logs)} logs")

        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")

    @staticmethod
    def detect_anomaly(db: Session, log_id: int, log_entry: Log) -> Anomaly:
        """Detect anomalies using multiple algorithms."""
        try:
            scores = {
                'statistical': AnomalyService.detect_statistical_anomaly(db, log_id, log_entry),
                'spike': AnomalyService.detect_spike_anomaly(db, log_id, log_entry),
                'pattern': AnomalyService.detect_pattern_anomaly(db, log_id, log_entry),
                'isolation_forest': AnomalyService.detect_isolation_forest_anomaly(db, log_id),
            }

            final_score = np.mean(list(scores.values()))
            is_anomaly = final_score > settings.anomaly_threshold

            anomaly = Anomaly(
                log_id=log_id,
                anomaly_score=float(final_score),
                is_anomaly=is_anomaly,
                model_version="v1.0",
                algorithm="ensemble",
                features_json=scores,
            )

            db.add(anomaly)
            db.commit()
            db.refresh(anomaly)

            logger.info(f"Anomaly detected for log {log_id}: score={final_score}, is_anomaly={is_anomaly}")
            return anomaly

        except Exception as e:
            db.rollback()
            logger.error(f"Anomaly detection failed: {str(e)}")
            raise AnomalyDetectionException(f"Anomaly detection failed: {str(e)}")

    @staticmethod
    def get_anomalies(db: Session, filters: AnomalyFilterRequest) -> Tuple[List[AnomalyResponse], int]:
        """Get anomalies with filtering and pagination."""
        query = db.query(Anomaly)

        if filters.algorithm:
            query = query.filter(Anomaly.algorithm == filters.algorithm.value)
        if filters.is_anomaly is not None:
            query = query.filter(Anomaly.is_anomaly == filters.is_anomaly)

        query = query.filter(
            Anomaly.anomaly_score >= filters.min_score,
            Anomaly.anomaly_score <= filters.max_score
        )

        if filters.start_date:
            query = query.filter(Anomaly.detected_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(Anomaly.detected_at <= filters.end_date)

        total = query.count()
        offset = (filters.page - 1) * filters.page_size
        anomalies = query.order_by(desc(Anomaly.detected_at)).offset(offset).limit(filters.page_size).all()

        responses = [AnomalyResponse.model_validate(anomaly) for anomaly in anomalies]
        return responses, total

    @staticmethod
    def get_anomaly_statistics(db: Session) -> Dict[str, Any]:
        """Get anomaly statistics."""
        total_logs = db.query(Log).count()
        total_anomalies = db.query(Anomaly).filter(Anomaly.is_anomaly == True).count()

        anomaly_percentage = (total_anomalies / total_logs * 100) if total_logs > 0 else 0

        anomalies = db.query(Anomaly).all()
        scores = [a.anomaly_score for a in anomalies] if anomalies else [0]

        return {
            'total_logs': total_logs,
            'total_anomalies': total_anomalies,
            'anomaly_percentage': anomaly_percentage,
            'average_score': float(np.mean(scores)),
            'max_score': float(np.max(scores)),
            'min_score': float(np.min(scores)),
        }
