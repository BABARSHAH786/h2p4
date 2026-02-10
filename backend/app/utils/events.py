"""Event publishing utilities using Dapr Pub/Sub.

This module provides functions to publish events to Kafka via Dapr Pub/Sub component.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.config import settings


DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "pubsub"


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


async def publish_event(
    topic: str,
    event_type: str,
    user_id: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Publish an event to Kafka via Dapr Pub/Sub.

    Args:
        topic: Kafka topic name (task-events, reminders, task-updates)
        event_type: Event type (task.created, task.updated, etc.)
        user_id: User ID associated with the event
        data: Event payload data
        metadata: Optional metadata (source_service, correlation_id, etc.)

    Returns:
        True if event was published successfully, False otherwise
    """
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": utcnow().isoformat(),
        "user_id": user_id,
        "data": data,
        "metadata": metadata or {
            "source_service": "chat-api",
            "correlation_id": None
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        # Log error but don't fail the main operation
        print(f"Failed to publish event to {topic}: {e}")
        return False


async def publish_task_created(task_id: int, user_id: str, task_data: Dict[str, Any]) -> bool:
    """Publish task.created event."""
    return await publish_event(
        topic="task-events",
        event_type="task.created",
        user_id=user_id,
        data={
            "task_id": task_id,
            **task_data
        }
    )


async def publish_task_updated(task_id: int, user_id: str, task_data: Dict[str, Any]) -> bool:
    """Publish task.updated event."""
    return await publish_event(
        topic="task-events",
        event_type="task.updated",
        user_id=user_id,
        data={
            "task_id": task_id,
            **task_data
        }
    )


async def publish_task_completed(task_id: int, user_id: str, task_data: Dict[str, Any]) -> bool:
    """Publish task.completed event."""
    return await publish_event(
        topic="task-events",
        event_type="task.completed",
        user_id=user_id,
        data={
            "task_id": task_id,
            **task_data
        }
    )


async def publish_task_deleted(task_id: int, user_id: str, task_data: Dict[str, Any]) -> bool:
    """Publish task.deleted event."""
    return await publish_event(
        topic="task-events",
        event_type="task.deleted",
        user_id=user_id,
        data={
            "task_id": task_id,
            **task_data
        }
    )


async def publish_reminder_scheduled(
    task_id: int,
    user_id: str,
    reminder_time: str,
    task_data: Dict[str, Any]
) -> bool:
    """Publish reminder.scheduled event."""
    return await publish_event(
        topic="reminders",
        event_type="reminder.scheduled",
        user_id=user_id,
        data={
            "task_id": task_id,
            "reminder_time": reminder_time,
            **task_data
        }
    )
