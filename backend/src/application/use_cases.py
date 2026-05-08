from src.domain.entities import SensorData
from src.domain.repositories import SensorRepository
from datetime import datetime, UTC

class StoreSensorDataUseCase:
    def __init__(self, repository: SensorRepository):
        self.repository = repository

    def execute(self, temperature: float, humidity: float, state: str) -> SensorData:
        sensor_data = SensorData(
            temperature=temperature,
            humidity=humidity,
            state=state,
            timestamp=datetime.now(UTC)
        )
        self.repository.save(sensor_data)
        return sensor_data
