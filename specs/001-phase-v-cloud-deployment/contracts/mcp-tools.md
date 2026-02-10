# MCP Tool Contracts - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Overview

Model Context Protocol (MCP) tools provide the interface between the OpenAI Agents SDK and the task management system. Phase V updates existing tools and adds new capabilities for advanced features.

## Tool Definitions

### 1. add_task (Updated)

**Purpose**: Create a new task with advanced features (priorities, tags, due dates, reminders, recurrence)

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title (required, max 500 chars)",
      "maxLength": 500
    },
    "description": {
      "type": "string",
      "description": "Detailed task description (optional)",
      "default": null
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Task priority level (default: medium)",
      "default": "medium"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 50
      },
      "description": "Custom labels for categorization (0-10 tags)",
      "maxItems": 10,
      "default": []
    },
    "due_at": {
      "type": "string",
      "format": "date-time",
      "description": "Due date and time in ISO-8601 format (optional)",
      "default": null
    },
    "reminder_minutes_before": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10080,
      "description": "Minutes before due_at to send reminder (default: 60)",
      "default": 60
    },
    "recurrence": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly", "yearly"],
      "description": "Recurrence pattern (default: none)",
      "default": "none"
    },
    "recurrence_end_date": {
      "type": "string",
      "format": "date-time",
      "description": "When to stop creating recurring tasks (optional)",
      "default": null
    }
  },
  "required": ["title"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the created task"
    },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "priority": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } },
    "due_at": { "type": "string", "format": "date-time" },
    "reminder_minutes_before": { "type": "integer" },
    "recurrence": { "type": "string" },
    "recurrence_end_date": { "type": "string", "format": "date-time" },
    "completed": { "type": "boolean" },
    "created_at": { "type": "string", "format": "date-time" }
  }
}
```

**Side Effects**:
- Creates task in database
- Publishes `task.created` event to `task-events` topic
- If `due_at` is set, publishes `reminder.scheduled` event to `reminders` topic

**Example Usage**:
```python
# Agent invokes tool
result = add_task(
    title="Client presentation",
    description="Prepare slides for Q1 review",
    priority="high",
    tags=["work", "urgent"],
    due_at="2026-02-15T14:00:00Z",
    reminder_minutes_before=60,
    recurrence="none"
)

# Returns
{
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Client presentation",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_at": "2026-02-15T14:00:00Z",
    "reminder_minutes_before": 60,
    "recurrence": "none",
    "completed": false,
    "created_at": "2026-02-10T14:30:00Z"
}
```

**Validation Rules**:
- `title` must be non-empty
- `tags` array max 10 items, each max 50 chars
- `due_at` must be in the future
- `reminder_minutes_before` must be 1-10080 (1 week)
- If `recurrence != "none"`, `due_at` is required
- If `recurrence_end_date` is set, it must be after `due_at`

---

### 2. update_task (Updated)

**Purpose**: Update an existing task's properties

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Task identifier (required)"
    },
    "title": {
      "type": "string",
      "description": "New task title (optional)",
      "maxLength": 500
    },
    "description": {
      "type": "string",
      "description": "New task description (optional)"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "New priority level (optional)"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string", "maxLength": 50 },
      "description": "New tags (replaces existing, optional)",
      "maxItems": 10
    },
    "due_at": {
      "type": "string",
      "format": "date-time",
      "description": "New due date (optional)"
    },
    "reminder_minutes_before": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10080,
      "description": "New reminder interval (optional)"
    },
    "recurrence": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly", "yearly"],
      "description": "New recurrence pattern (optional)"
    },
    "recurrence_end_date": {
      "type": "string",
      "format": "date-time",
      "description": "New recurrence end date (optional)"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "string", "format": "uuid" },
    "updated_fields": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of fields that were modified"
    },
    "task": {
      "type": "object",
      "description": "Updated task object"
    }
  }
}
```

**Side Effects**:
- Updates task in database
- Publishes `task.updated` event to `task-events` topic
- If `due_at` changed, reschedules reminder (publishes new `reminder.scheduled` event)

**Example Usage**:
```python
result = update_task(
    task_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    priority="high",
    tags=["work", "urgent", "client"]
)

# Returns
{
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "updated_fields": ["priority", "tags"],
    "task": { /* full task object */ }
}
```

---

### 3. list_tasks (Updated)

**Purpose**: List tasks with filtering and sorting

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "description": "Filter by completion status (default: all)",
      "default": "all"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Filter by priority level (optional)"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Filter by tags (tasks must have ALL specified tags)"
    },
    "due_after": {
      "type": "string",
      "format": "date-time",
      "description": "Filter tasks due after this date (optional)"
    },
    "due_before": {
      "type": "string",
      "format": "date-time",
      "description": "Filter tasks due before this date (optional)"
    },
    "order_by": {
      "type": "string",
      "enum": ["created_at", "due_date", "priority", "title"],
      "description": "Sort field (default: created_at)",
      "default": "created_at"
    },
    "order_direction": {
      "type": "string",
      "enum": ["asc", "desc"],
      "description": "Sort direction (default: desc for created_at, asc for others)",
      "default": "desc"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum number of tasks to return (default: 50)",
      "default": 50
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "description": "Task object with all fields"
      }
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of tasks matching filters"
    },
    "filters_applied": {
      "type": "object",
      "description": "Summary of applied filters"
    }
  }
}
```

**Example Usage**:
```python
# List high priority work tasks due this week
result = list_tasks(
    status="pending",
    priority="high",
    tags=["work"],
    due_after="2026-02-10T00:00:00Z",
    due_before="2026-02-17T23:59:59Z",
    order_by="due_date",
    order_direction="asc"
)

# Returns
{
    "tasks": [
        { "task_id": "...", "title": "Client presentation", ... },
        { "task_id": "...", "title": "Budget review", ... }
    ],
    "total_count": 2,
    "filters_applied": {
        "status": "pending",
        "priority": "high",
        "tags": ["work"],
        "due_range": "2026-02-10 to 2026-02-17"
    }
}
```

---

### 4. search_tasks (NEW)

**Purpose**: Search tasks by keyword in title and description

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "keyword": {
      "type": "string",
      "description": "Search keyword (required, min 2 chars)",
      "minLength": 2
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "description": "Filter by completion status (default: all)",
      "default": "all"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "description": "Maximum number of results (default: 20)",
      "default": 20
    }
  },
  "required": ["keyword"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "description": "Task object with all fields"
      }
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of matching tasks"
    },
    "keyword": {
      "type": "string",
      "description": "Search keyword used"
    }
  }
}
```

**Example Usage**:
```python
result = search_tasks(
    keyword="presentation",
    status="pending"
)

# Returns
{
    "tasks": [
        { "task_id": "...", "title": "Client presentation", ... },
        { "task_id": "...", "title": "Prepare presentation slides", ... }
    ],
    "total_count": 2,
    "keyword": "presentation"
}
```

**Search Behavior**:
- Case-insensitive
- Partial matching (substring search)
- Searches both title and description fields
- Uses database indexes for performance

---

### 5. complete_task (Unchanged)

**Purpose**: Mark a task as completed

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Task identifier (required)"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "string", "format": "uuid" },
    "completed": { "type": "boolean", "const": true },
    "completed_at": { "type": "string", "format": "date-time" }
  }
}
```

**Side Effects**:
- Updates task.completed = true in database
- Publishes `task.completed` event to `task-events` topic
- If task has `recurrence != "none"`, Recurring Task Service will create next occurrence

---

### 6. delete_task (Unchanged)

**Purpose**: Delete a task permanently

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "Task identifier (required)"
    }
  },
  "required": ["task_id"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "string", "format": "uuid" },
    "deleted": { "type": "boolean", "const": true },
    "deleted_at": { "type": "string", "format": "date-time" }
  }
}
```

**Side Effects**:
- Deletes task from database
- Publishes `task.deleted` event to `task-events` topic
- Cancels any scheduled reminders for this task

---

## Natural Language Understanding

The OpenAI Agents SDK should infer parameters from natural language:

**Priority Inference**:
- "urgent", "critical", "ASAP" → `priority: "high"`
- "when you get a chance", "low priority" → `priority: "low"`
- Default → `priority: "medium"`

**Tag Inference**:
- "work meeting" → `tags: ["work", "meeting"]`
- "grocery shopping" → `tags: ["personal", "shopping"]`
- "urgent client task" → `tags: ["urgent", "client"]`

**Due Date Parsing**:
- "tomorrow at 3 PM" → calculate ISO-8601 datetime
- "next Friday" → calculate next Friday's date
- "in 2 hours" → calculate datetime 2 hours from now

**Recurrence Parsing**:
- "every day" → `recurrence: "daily"`
- "weekly on Monday" → `recurrence: "weekly"`
- "monthly" → `recurrence: "monthly"`
- "every year" → `recurrence: "yearly"`

**Example Natural Language Inputs**:

```
User: "Add a task 'Client presentation' tagged with work, high priority, due Friday 3 PM"
→ add_task(
    title="Client presentation",
    priority="high",
    tags=["work"],
    due_at="2026-02-14T15:00:00Z"
)

User: "Show me all high priority work tasks"
→ list_tasks(
    status="pending",
    priority="high",
    tags=["work"]
)

User: "Find tasks about presentation"
→ search_tasks(keyword="presentation")

User: "Add weekly team standup every Monday at 10 AM"
→ add_task(
    title="Team standup",
    recurrence="weekly",
    due_at="2026-02-17T10:00:00Z"  # Next Monday
)
```

## Error Handling

**Validation Errors**:
```json
{
  "error": "ValidationError",
  "message": "Title is required",
  "field": "title"
}
```

**Not Found Errors**:
```json
{
  "error": "NotFoundError",
  "message": "Task not found",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Permission Errors**:
```json
{
  "error": "PermissionError",
  "message": "You don't have permission to access this task",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## Performance Expectations

- **add_task**: <100ms (p95)
- **update_task**: <100ms (p95)
- **list_tasks**: <200ms (p95) for 1000 tasks
- **search_tasks**: <300ms (p95) for 10,000 tasks
- **complete_task**: <100ms (p95)
- **delete_task**: <100ms (p95)

## Testing

**Unit Tests**:
```python
def test_add_task_with_priority_and_tags():
    result = add_task(
        title="Test task",
        priority="high",
        tags=["test", "urgent"]
    )
    assert result["priority"] == "high"
    assert result["tags"] == ["test", "urgent"]

def test_list_tasks_filters_by_priority():
    add_task(title="High priority", priority="high")
    add_task(title="Low priority", priority="low")

    result = list_tasks(priority="high")
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "High priority"

def test_search_tasks_finds_keyword():
    add_task(title="Client presentation")
    add_task(title="Team meeting")

    result = search_tasks(keyword="presentation")
    assert result["total_count"] == 1
    assert result["tasks"][0]["title"] == "Client presentation"
```

## Summary

Phase V updates 3 existing MCP tools (add_task, update_task, list_tasks) and adds 1 new tool (search_tasks) to support advanced features:
- Task priorities (high/medium/low)
- Custom tags for categorization
- Due dates with reminders
- Recurring tasks (daily/weekly/monthly/yearly)
- Advanced filtering and sorting
- Keyword search

All tools publish events to Kafka for event-driven architecture integration.
