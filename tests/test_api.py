import pytest
from fastapi import status

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_analyze_pr(client, sample_pr_data):
    """Test PR analysis endpoint"""
    response = client.post(
        "/api/v1/analyze-pr",
        json=sample_pr_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_get_status(client):
    """Test status endpoint"""
    response = client.get("/api/v1/status/test-task-id")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data

