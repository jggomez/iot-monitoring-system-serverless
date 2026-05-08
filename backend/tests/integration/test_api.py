import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import base64
import json
from src.main import app
from src.interfaces.api import get_use_case
from src.application.use_cases import StoreSensorDataUseCase
from src.domain.repositories import SensorRepository

client = TestClient(app)

def test_store_sensor_data_api_success():
    # Arrange
    mock_repository = MagicMock(spec=SensorRepository)
    mock_use_case = StoreSensorDataUseCase(mock_repository)
    
    # Override dependency
    app.dependency_overrides[get_use_case] = lambda: mock_use_case
    
    payload = {
        "temperature": 45.6,
        "humidity": 45.6,
        "state": "generated"
    }
    
    # Act
    response = client.post("/api/v1/sensors", json=payload)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 45.6
    assert data["humidity"] == 45.6
    assert data["state"] == "generated"
    assert "timestamp" in data
    mock_repository.save.assert_called_once()
    
    # Cleanup
    app.dependency_overrides.clear()

def test_store_pubsub_data_api_success():
    # Arrange
    mock_repository = MagicMock(spec=SensorRepository)
    mock_use_case = StoreSensorDataUseCase(mock_repository)
    
    # Override dependency
    app.dependency_overrides[get_use_case] = lambda: mock_use_case
    
    sensor_data = {
        "temperature": 45.6,
        "humidity": 45.6,
        "state": "generated"
    }
    # Encode data to base64
    base64_data = base64.b64encode(json.dumps(sensor_data).encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": {
            "data": base64_data,
            "messageId": "12345",
            "publishTime": "2024-01-01T00:00:00Z"
        }
    }
    
    # Act
    response = client.post("/api/v1/sensors/pubsub", json=payload)
    
    # Assert
    assert response.status_code == 204
    mock_repository.save.assert_called_once()
    
    # Cleanup
    app.dependency_overrides.clear()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
