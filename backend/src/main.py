from fastapi import FastAPI
from src.interfaces.api import router as sensor_router
import logging
import json
import sys
from contextlib import asynccontextmanager
from src.infrastructure.mqtt_client import mqtt_service

class CloudLoggingFormatter(logging.Formatter):
    def format(self, record):
        try:
            message = record.getMessage()
        except Exception:
            message = str(record.msg)

        # Standard log entry for Google Cloud Logging
        log_entry = {
            "severity": record.levelname,
            "message": message,
            "logger": record.name,
            "timestamp": self.formatTime(record, self.datefmt),
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }
        }

        # Add trace and span if present (for Cloud Trace integration)
        if hasattr(record, 'trace'):
            log_entry['logging.googleapis.com/trace'] = record.trace
        if hasattr(record, 'spanId'):
            log_entry['logging.googleapis.com/spanId'] = record.spanId

        # Add extra fields from record.__dict__ that are not standard LogRecord attributes
        standard_attrs = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                try:
                    # Test JSON serialization
                    json.dumps(value)
                    log_entry[key] = value
                except (TypeError, OverflowError):
                    log_entry[key] = str(value)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

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
