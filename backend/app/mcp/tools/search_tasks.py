from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlmodel import select
from app.models.task import Task


async def search_tasks(
    user_id: str,
    keyword: str,
    session: AsyncSession = None
):
    """
    Search tasks by keyword in title and description.

    Args:
        user_id: The ID of the user whose tasks to search
        keyword: Search keyword
        session: Database session

    Returns:
        Dict with success status, data, and message
    """
    try:
        print(f"Searching tasks for user_id: {user_id}, keyword: {keyword}")

        # Build search query with case-insensitive LIKE
        query = select(Task).where(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(f"%{keyword}%"),
                Task.description.ilike(f"%{keyword}%")
            )
        ).order_by(Task.created_at.desc())

        # Execute the query asynchronously
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Convert tasks to dictionaries
        tasks_data = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority,
                "tags": task.tags,
                "due_at": task.due_date.isoformat() if task.due_date else None,
                "recurrence": task.recurrence,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            tasks_data.append(task_dict)

        print(f"Found {len(tasks_data)} tasks matching keyword '{keyword}'")

        return {
            "success": True,
            "data": {
                "tasks": tasks_data,
                "count": len(tasks_data),
                "keyword": keyword
            },
            "message": f"Found {len(tasks_data)} tasks matching '{keyword}'"
        }

    except Exception as e:
        print(f"Error searching tasks: {str(e)}")
        return {
            "success": False,
            "data": {
                "tasks": [],
                "count": 0,
                "keyword": keyword
            },
            "message": f"Error searching tasks: {str(e)}"
        }
