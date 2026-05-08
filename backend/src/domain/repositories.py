from abc import ABC, abstractmethod
from src.domain.entities import SensorData

class SensorRepository(ABC):
    @abstractmethod
    def save(self, sensor_data: SensorData) -> None:
        pass
