import io
from datetime import datetime

def test_upload_logs(client):
    log_content = "2023-01-01T12:00:00 INFO application app_main - Application started\n"
    log_content += "2023-01-01T12:01:00 ERROR application app_main - An error occurred"

    files = {"file": ("test.log", io.BytesIO(log_content.encode()), "text/plain")}
    response = client.post("/api/logs/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 2

def test_ingest_single_log(client):
    log_data = {
        "timestamp": "2023-01-01T12:05:00",
        "level": "WARNING",
        "message": "High memory usage",
        "source": "platform",
        "service": "monitor"
    }
    response = client.post("/api/logs/ingest", json=log_data)

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == "WARNING"
    assert data["message"] == "High memory usage"

def test_get_logs(client):
    # Upload some logs first
    log_content = "2023-01-01T12:00:00 INFO app s1 - m1\n"
    files = {"file": ("test.log", io.BytesIO(log_content.encode()), "text/plain")}
    client.post("/api/logs/upload", files=files)

    response = client.get("/api/logs/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["logs"]) >= 1

def test_get_log_by_id(client):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": "Specific log message",
        "source": "application",
        "service": "s1"
    }
    ingest_resp = client.post("/api/logs/ingest", json=log_data)
    assert ingest_resp.status_code == 200, ingest_resp.text
    log_id = ingest_resp.json()["id"]

    response = client.get(f"/api/logs/{log_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Specific log message"
    assert response.json()["id"] == log_id

def test_get_log_statistics(client):
    response = client.get("/api/logs/statistics/summary")
    assert response.status_code == 200
    assert response.json()["success"] is True
