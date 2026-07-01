from datetime import datetime
from app.services.log_service import LogService
from app.schemas.log_schemas import LogCreate, LogLevel, LogSource

def test_ingest_log_service(db):
    log_data = LogCreate(
        timestamp=datetime.utcnow(),
        level=LogLevel.INFO,
        message="Service test message",
        source=LogSource.APPLICATION,
        service="test-service"
    )
    log = LogService.ingest_log(db, log_data)
    assert log.id is not None
    assert log.message == "Service test message"

def test_parse_log_file_text():
    content = b"Line 1\nLine 2 ERROR Something failed"
    logs = LogService.parse_log_file(content, "test.log")
    assert len(logs) == 2
    assert logs[1]["level"] == "ERROR"

def test_get_log_statistics_service(db):
    log_data = LogCreate(
        timestamp=datetime.utcnow(),
        level=LogLevel.ERROR,
        message="Error for stats",
        source=LogSource.API,
        service="test-service"
    )
    LogService.ingest_log(db, log_data)
    stats = LogService.get_log_statistics(db)
    assert stats["total_logs"] >= 1
    assert "ERROR" in stats["by_level"]
