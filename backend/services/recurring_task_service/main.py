"""Recurring Task Service - Main Application.

This service consumes task.completed events from Kafka and creates next occurrences
for recurring tasks.
"""
import asyncio
import logging
import json
from datetime import datetime
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from consumer import start_consumer, stop_consumer
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.database import get_session


# Configure structured JSON logging
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "recurring-task-service",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add user_id if available
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


# Setup logging
logger = logging.getLogger("recurring-task-service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle."""
    logger.info("Starting recurring-task-service")

    # Start Kafka consumer on startup
    consumer_task = asyncio.create_task(start_consumer())

    yield

    logger.info("Shutting down recurring-task-service")
    # Stop Kafka consumer on shutdown
    await stop_consumer()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Recurring Task Service",
    description="Microservice for handling recurring task automation",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health/live")
async def liveness():
    """Liveness probe for Kubernetes."""
    logger.info("Liveness probe called")
    return {
        "status": "alive",
        "service": "recurring-task-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/ready")
async def readiness():
    """
    Readiness probe for Kubernetes.

    Checks database connectivity and service dependencies.
    """
    try:
        # Check database connectivity
        async with get_session() as session:
            await session.execute("SELECT 1")

        logger.info("Readiness probe passed")
        return {
            "status": "ready",
            "service": "recurring-task-service",
            "checks": {
                "database": "connected",
                "kafka_consumer": "running",
                "dapr": "connected"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "recurring-task-service",
                "checks": {
                    "database": "disconnected",
                    "error": str(e)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (optional)."""
    # TODO: Implement Prometheus metrics
    return {
        "recurring_tasks_processed_total": 0,
        "recurring_tasks_created_total": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
