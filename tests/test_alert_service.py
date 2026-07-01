from datetime import datetime
from app.services.alert_service import AlertService
from app.services.log_service import LogService
from app.schemas.log_schemas import LogCreate, LogLevel, LogSource

def test_detect_and_create_alerts_service(db):
    log_data = LogCreate(
        timestamp=datetime.utcnow(),
        level=LogLevel.CRITICAL,
        message="Alert service test",
        source=LogSource.SYSTEM,
        service="test-service"
    )
    log = LogService.ingest_log(db, log_data)
    alerts = AlertService.detect_and_create_alerts(db, log)
    assert len(alerts) >= 1
    assert alerts[0].severity == "CRITICAL"

def test_resolve_alert_service(db):
    alert = AlertService.create_alert(
        db, log_id=None, alert_type="test", severity="LOW", message="Test alert"
    )
    resolved = AlertService.resolve_alert(db, alert.id, "Resolving test alert")
    assert resolved.resolved_at is not None

def test_get_alert_statistics_service(db):
    stats = AlertService.get_alert_statistics(db)
    assert stats.total_alerts >= 0
