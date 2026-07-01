from datetime import datetime
from app.services.anomaly_service import AnomalyService
from app.services.log_service import LogService
from app.schemas.log_schemas import LogCreate, LogLevel, LogSource

def test_detect_anomaly_service(db):
    # Create logs to detect anomaly
    log_data = LogCreate(
        timestamp=datetime.utcnow(),
        level=LogLevel.ERROR,
        message="Anomaly test error",
        source=LogSource.APPLICATION,
        service="test-service"
    )

    log = LogService.ingest_log(db, log_data)
    anomaly = AnomalyService.detect_anomaly(db, log.id, log)
    assert anomaly.id is not None
    assert anomaly.log_id == log.id

def test_get_anomaly_statistics_service(db):
    stats = AnomalyService.get_anomaly_statistics(db)
    assert "total_logs" in stats
    assert "total_anomalies" in stats
