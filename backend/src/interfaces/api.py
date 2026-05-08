import logging
from fastapi import APIRouter, Depends, HTTPException
from src.interfaces.schemas import SensorDataRequest, SensorDataResponse, PubSubRequest
from src.application.use_cases import StoreSensorDataUseCase
from src.infrastructure.firestore_repository import FirestoreSensorRepository

router = APIRouter()
logger = logging.getLogger(__name__)

_repository = FirestoreSensorRepository()


def get_use_case():
    return StoreSensorDataUseCase(_repository)


@router.post("/sensors", response_model=SensorDataResponse)
async def store_sensor_data(
    request: SensorDataRequest, use_case: StoreSensorDataUseCase = Depends(get_use_case)
):
    try:
        stored_data = use_case.execute(
            temperature=request.temperature,
            humidity=request.humidity,
            state=request.state,
        )
        logger.info("Successfully stored sensor data from direct API")
        return SensorDataResponse(
            temperature=stored_data.temperature,
            humidity=stored_data.humidity,
            state=stored_data.state,
            timestamp=stored_data.timestamp.isoformat(),
        )
    except Exception as e:
        logger.error(f"Error storing sensor data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensors/pubsub", status_code=204)
async def store_pubsub_data(
    request: PubSubRequest, use_case: StoreSensorDataUseCase = Depends(get_use_case)
):
    try:
        data = request.message.decoded_data
        logger.info(f"Received Pub/Sub message: {data}")

        state = data.get("state") or data.get("status") or "unknown"

        use_case.execute(
            temperature=data.get("temperature", 0.0),
            humidity=data.get("humidity", 0.0),
            state=state,
        )
        return
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}"
        )
