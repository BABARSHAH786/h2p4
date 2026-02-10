"""Dapr Jobs API service for scheduling reminders.

This module provides functions to schedule and manage reminder jobs using Dapr Jobs API.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional


DAPR_HTTP_PORT = 3500
JOBS_COMPONENT = "jobs"


async def schedule_reminder(
    task_id: int,
    user_id: str,
    reminder_time: datetime,
    task_title: str,
    callback_url: str = "http://localhost:8000/api/jobs/reminder-callback"
) -> bool:
    """
    Schedule a reminder job using Dapr Jobs API.

    Args:
        task_id: Task ID
        user_id: User ID
        reminder_time: When to trigger the reminder
        task_title: Task title for the reminder
        callback_url: URL to call when reminder triggers

    Returns:
        True if reminder was scheduled successfully, False otherwise
    """
    job_name = f"reminder-task-{task_id}"

    # Calculate schedule time in ISO format
    schedule_time = reminder_time.isoformat()

    job_data = {
        "schedule": f"@once {schedule_time}",
        "repeats": 1,
        "data": {
            "task_id": task_id,
            "user_id": user_id,
            "task_title": task_title,
            "callback_url": callback_url
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}",
                json=job_data,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Failed to schedule reminder for task {task_id}: {e}")
        return False


async def cancel_reminder(task_id: int) -> bool:
    """
    Cancel a scheduled reminder job.

    Args:
        task_id: Task ID

    Returns:
        True if reminder was cancelled successfully, False otherwise
    """
    job_name = f"reminder-task-{task_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}",
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Failed to cancel reminder for task {task_id}: {e}")
        return False


async def get_reminder_status(task_id: int) -> Optional[dict]:
    """
    Get the status of a scheduled reminder job.

    Args:
        task_id: Task ID

    Returns:
        Job status dict if found, None otherwise
    """
    job_name = f"reminder-task-{task_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Failed to get reminder status for task {task_id}: {e}")
        return None
