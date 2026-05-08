from google.cloud import firestore
from src.domain.entities import SensorData
from src.domain.repositories import SensorRepository
import os

class FirestoreSensorRepository(SensorRepository):
    def __init__(self, collection_name: str = "sensor_data"):
        self.db = firestore.Client()
        self.collection = self.db.collection(collection_name)

    def save(self, sensor_data: SensorData) -> None:
        self.collection.add(sensor_data.to_dict())
