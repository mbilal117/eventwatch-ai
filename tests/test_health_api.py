def test_get_health(client):
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "current" in data["data"]
    assert "health_score" in data["data"]["current"]

def test_get_health_score(client):
    response = client.get("/api/health/score")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "health_score" in data

def test_get_health_history(client):
    response = client.get("/api/health/history")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "history" in data
