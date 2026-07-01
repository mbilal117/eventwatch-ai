def test_get_alerts(client):
    # Alerts are created when logs are ingested
    log_data = {
        "timestamp": "2023-01-01T12:05:00",
        "level": "CRITICAL",
        "message": "System meltdown",
        "source": "platform",
        "service": "core"
    }
    client.post("/api/logs/ingest", json=log_data)

    # Manually check DB to see if alert was created if API returns empty
    response = client.get("/api/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_resolve_alert(client):
    log_data = {
        "timestamp": "2023-01-01T12:05:00",
        "level": "CRITICAL",
        "message": "Another critical error",
        "source": "platform",
        "service": "core"
    }
    client.post("/api/logs/ingest", json=log_data)

    alerts_resp = client.get("/api/alerts/")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()["alerts"]
    assert len(alerts) > 0
    alert_id = alerts[0]["id"]

    response = client.put(f"/api/alerts/{alert_id}/resolve", params={"notes": "Fixed it"})
    assert response.status_code == 200
    assert response.json()["resolved_at"] is not None

def test_get_alert_statistics(client):
    response = client.get("/api/alerts/statistics/summary")
    assert response.status_code == 200
    assert "total_alerts" in response.json()
