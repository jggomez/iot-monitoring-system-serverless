from fastapi import FastAPI
from src.interfaces.api import router as sensor_router
import logging
import json
import sys

class CloudLoggingFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "timestamp": self.formatTime(record, self.datefmt)
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(CloudLoggingFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])

app = FastAPI(title="IoT Sensor Data API")

app.include_router(sensor_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
