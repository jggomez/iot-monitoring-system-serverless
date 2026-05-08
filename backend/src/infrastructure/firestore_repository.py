from google.cloud import firestore
from src.domain.entities import SensorData
from src.domain.repositories import SensorRepository

class FirestoreSensorRepository(SensorRepository):
    def __init__(self, collection_name: str = "sensor_data"):
        self.db = firestore.Client()
        self.collection = self.db.collection(collection_name)

    def save(self, sensor_data: SensorData) -> None:
        self.collection.add(sensor_data.to_dict())

    def get_all(self) -> list[SensorData]:
        docs = self.collection.order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
        return [SensorData(**doc.to_dict()) for doc in docs]
