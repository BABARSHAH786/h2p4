"""Handler for recurring task logic.

This module calculates next occurrence dates and creates new tasks.
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.task import Task
from app.database import get_session
from app.utils.events import publish_task_created
from sqlalchemy.ext.asyncio import AsyncSession


async def handle_recurring_task_completion(event: dict):
    """
    Handle a task.completed event for a recurring task.

    Creates the next occurrence of the task based on recurrence pattern.
    """
    data = event.get("data", {})
    user_id = event.get("user_id")

    task_id = data.get("task_id")
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "medium")
    tags = data.get("tags", [])
    recurrence = data.get("recurrence", "none")
    recurrence_end_date = data.get("recurrence_end_date")
    due_at = data.get("due_at")
    reminder_minutes_before = data.get("reminder_minutes_before", 60)

    if not due_at:
        print(f"Task {task_id} has recurrence but no due_at, skipping")
        return

    # Calculate next occurrence date
    next_due_at = calculate_next_occurrence(due_at, recurrence)

    if not next_due_at:
        print(f"Failed to calculate next occurrence for task {task_id}")
        return

    # Check if we should stop creating occurrences
    if recurrence_end_date:
        end_date = datetime.fromisoformat(recurrence_end_date.replace('Z', '+00:00'))
        if next_due_at > end_date:
            print(f"Recurrence end date reached for task {task_id}, stopping")
            return

    # Create next occurrence in database
    try:
        async with get_session() as session:
            new_task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=next_due_at,
                recurrence=recurrence,
                recurrence_end_date=datetime.fromisoformat(recurrence_end_date.replace('Z', '+00:00')) if recurrence_end_date else None,
                reminder_minutes_before=reminder_minutes_before,
                completed=False,
                reminder_sent=False
            )

            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            print(f"Created next occurrence for task {task_id}: new task ID {new_task.id}")

            # Publish task.created event
            task_data = {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "priority": new_task.priority,
                "tags": new_task.tags,
                "due_at": new_task.due_date.isoformat() if new_task.due_date else None,
                "recurrence": new_task.recurrence,
                "recurrence_end_date": new_task.recurrence_end_date.isoformat() if new_task.recurrence_end_date else None,
                "reminder_minutes_before": new_task.reminder_minutes_before,
                "completed": new_task.completed,
                "reminder_sent": new_task.reminder_sent
            }

            await publish_task_created(new_task.id, user_id, task_data)

    except Exception as e:
        print(f"Error creating next occurrence for task {task_id}: {e}")


def calculate_next_occurrence(due_at_str: str, recurrence: str) -> Optional[datetime]:
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        due_at_str: ISO format datetime string
        recurrence: Recurrence pattern (daily, weekly, monthly, yearly)

    Returns:
        Next occurrence datetime or None if calculation fails
    """
    try:
        due_at = datetime.fromisoformat(due_at_str.replace('Z', '+00:00'))

        if recurrence == "daily":
            return due_at + timedelta(days=1)
        elif recurrence == "weekly":
            return due_at + timedelta(weeks=1)
        elif recurrence == "monthly":
            return due_at + relativedelta(months=1)
        elif recurrence == "yearly":
            return due_at + relativedelta(years=1)
        else:
            return None

    except Exception as e:
        print(f"Error calculating next occurrence: {e}")
        return None
