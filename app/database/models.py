"""SQLAlchemy ORM models for EventWatch AI."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Log(Base):
    """Log entry model."""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(50), index=True)  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text)
    source = Column(String(255), index=True)  # application, platform, API
    service = Column(String(255), index=True)
    metadata_json = Column(JSON, nullable=True)
    file_source = Column(String(255), nullable=True)  # Filename
    raw_line = Column(Text, nullable=True)

    alerts = relationship("Alert", back_populates="log", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="log", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_logs_timestamp_level', 'timestamp', 'level'),
        Index('idx_logs_timestamp_source', 'timestamp', 'source'),
        Index('idx_logs_timestamp_service', 'timestamp', 'service'),
    )


class Alert(Base):
    """Alert model."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("logs.id"), nullable=True)
    alert_type = Column(String(50), index=True)  # spike, pattern, rate_increase, anomaly
    severity = Column(String(20), index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    message = Column(Text)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    webhook_sent = Column(Boolean, default=False)
    webhook_response = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)

    log = relationship("Log", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_alerts_triggered_at', 'triggered_at'),
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_alert_type', 'alert_type'),
    )


class Anomaly(Base):
    """Anomaly detection result model."""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("logs.id"))
    anomaly_score = Column(Float)  # 0.0 to 1.0
    is_anomaly = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String(50))
    features_json = Column(JSON, nullable=True)
    algorithm = Column(String(50))  # isolation_forest, statistical, spike, pattern

    log = relationship("Log", back_populates="anomalies")

    __table_args__ = (
        Index('idx_anomalies_detected_at', 'detected_at'),
        Index('idx_anomalies_is_anomaly', 'is_anomaly'),
    )


class AlertHistory(Base):
    """Alert status history model."""
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    status = Column(String(20))  # created, escalated, resolved, acknowledged
    changed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    alert = relationship("Alert", back_populates="history")

    __table_args__ = (
        Index('idx_alert_history_changed_at', 'changed_at'),
    )


class SystemHealth(Base):
    """System health metrics model."""
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    health_score = Column(Float)  # 0-100
    total_logs = Column(Integer)
    error_count = Column(Integer)
    warning_count = Column(Integer)
    anomaly_count = Column(Integer)
    active_alerts = Column(Integer)
    error_rate = Column(Float)  # percentage
    metadata_json = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_system_health_timestamp', 'timestamp'),
    )
