import io

def test_get_anomalies(client):
    # Ingest a log to trigger anomaly detection
    log_data = {
        "timestamp": "2023-01-01T12:05:00",
        "level": "ERROR",
        "message": "Critical failure",
        "source": "platform",
        "service": "api"
    }
    client.post("/api/logs/ingest", json=log_data)

    response = client.get("/api/anomalies/")
    assert response.status_code == 200
    data = response.json()
    # It might take some logs to train Isolation Forest,
    # but detect_anomaly should still return an Anomaly record (ensemble)
    assert data["total"] >= 1

def test_get_anomaly_statistics(client):
    response = client.get("/api/anomalies/statistics/summary")
    assert response.status_code == 200
    assert "total_anomalies" in response.json()
