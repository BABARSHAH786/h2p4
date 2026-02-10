"""Jobs callback endpoints for Dapr Jobs API.

This module handles callbacks from Dapr Jobs API for scheduled reminders.
"""
from fastapi import APIRouter, Request
from app.utils.events import publish_event
from datetime import datetime

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/reminder-callback")
async def reminder_callback(request: Request):
    """
    Callback endpoint for reminder jobs triggered by Dapr Jobs API.

    This endpoint is called by Dapr when a scheduled reminder job fires.
    It publishes a reminder.triggered event to Kafka.
    """
    try:
        # Get job data from request
        job_data = await request.json()

        task_id = job_data.get("task_id")
        user_id = job_data.get("user_id")
        task_title = job_data.get("task_title")

        if not task_id or not user_id:
            return {"success": False, "message": "Missing required fields"}

        # Publish reminder.triggered event to Kafka
        await publish_event(
            topic="reminders",
            event_type="reminder.triggered",
            user_id=user_id,
            data={
                "task_id": task_id,
                "title": task_title,
                "triggered_at": datetime.utcnow().isoformat()
            },
            metadata={
                "source_service": "chat-api",
                "trigger_type": "scheduled_job"
            }
        )

        print(f"Reminder triggered for task {task_id}, event published to Kafka")

        return {
            "success": True,
            "message": f"Reminder triggered for task {task_id}"
        }

    except Exception as e:
        print(f"Error in reminder callback: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """Health check endpoint for jobs service."""
    return {
        "status": "healthy",
        "service": "jobs-api",
        "timestamp": datetime.utcnow().isoformat()
    }
