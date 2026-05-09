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

import csv
import io

class ExportSensorDataCsvUseCase:
    def __init__(self, repository: SensorRepository):
        self.repository = repository

    def execute(self) -> str:
        data = self.repository.get_all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "temperature", "humidity", "state"])
        for entry in data:
            writer.writerow([entry.timestamp.isoformat(), entry.temperature, entry.humidity, entry.state])

        return output.getvalue()

class SendCommandUseCase:
    def __init__(self, mqtt_service, topic: str):
        self.mqtt_service = mqtt_service
        self.topic = topic

    def execute(self, status: str):
        message = {"status": status}
        return self.mqtt_service.publish(self.topic, message)
