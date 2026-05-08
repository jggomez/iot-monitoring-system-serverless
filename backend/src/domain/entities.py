from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional

@dataclass
class SensorData:
    temperature: float
    humidity: float
    state: str
    timestamp: Optional[datetime] = None

    def to_dict(self):
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "state": self.state,
            "timestamp": self.timestamp or datetime.now(UTC)
        }
