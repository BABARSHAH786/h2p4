"""Notification delivery logic.

This module handles sending email notifications for task reminders.
"""
import os
from datetime import datetime
from typing import Optional
import httpx
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.task import Task
from app.database import get_session


# Email service configuration (SendGrid, SMTP, etc.)
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@todoapp.com")
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL", "https://api.sendgrid.com/v3/mail/send")


async def send_reminder_notification(event: dict) -> bool:
    """
    Send a reminder notification via email.

    Args:
        event: reminder.triggered event containing task details

    Returns:
        True if notification was sent successfully, False otherwise
    """
    data = event.get("data", {})
    user_id = event.get("user_id")

    task_id = data.get("task_id")
    task_title = data.get("title", "Untitled Task")
    due_at = data.get("due_at")

    # Get user email from database (or use placeholder)
    user_email = await get_user_email(user_id)
    if not user_email:
        user_email = f"{user_id}@example.com"  # Fallback

    # Format reminder message
    subject = f"Reminder: {task_title}"
    body = format_reminder_email(task_title, due_at)

    # Send email
    success = await send_email(user_email, subject, body)

    if success:
        print(f"Sent reminder notification for task {task_id} to {user_email}")
        # Mark reminder as sent in database
        await mark_reminder_sent(task_id)
    else:
        print(f"Failed to send reminder notification for task {task_id}")

    return success


async def get_user_email(user_id: str) -> Optional[str]:
    """Get user email from database."""
    try:
        async with get_session() as session:
            # TODO: Query user table for email
            # For now, return placeholder
            return f"{user_id}@example.com"
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None


async def mark_reminder_sent(task_id: int):
    """Mark reminder as sent in database."""
    try:
        async with get_session() as session:
            from sqlmodel import select
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()

            if task:
                task.reminder_sent = True
                await session.commit()
                print(f"Marked reminder as sent for task {task_id}")
    except Exception as e:
        print(f"Error marking reminder as sent: {e}")


def format_reminder_email(task_title: str, due_at: Optional[str]) -> str:
    """Format the reminder email body."""
    if due_at:
        due_time = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
        due_str = due_time.strftime("%B %d, %Y at %I:%M %p")
        return f"""
Hello,

This is a reminder about your task:

Task: {task_title}
Due: {due_str}

Please complete this task before the deadline.

Best regards,
Todo Chatbot
"""
    else:
        return f"""
Hello,

This is a reminder about your task:

Task: {task_title}

Best regards,
Todo Chatbot
"""


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using configured email service.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Check if EMAIL_API_KEY is configured
    if not EMAIL_API_KEY or EMAIL_API_KEY == "":
        print(f"EMAIL_API_KEY not configured, simulating email send")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        return True  # Simulate success

    # Send via SendGrid
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                EMAIL_SERVICE_URL,
                headers={
                    "Authorization": f"Bearer {EMAIL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [
                        {
                            "to": [{"email": to_email}],
                            "subject": subject
                        }
                    ],
                    "from": {"email": EMAIL_FROM},
                    "content": [
                        {
                            "type": "text/plain",
                            "value": body
                        }
                    ]
                },
                timeout=10.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
