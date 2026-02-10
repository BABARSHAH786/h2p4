# Event Schemas - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Event Schema Standard

All events published to Kafka topics MUST follow this standardized structure:

```json
{
  "event_id": "uuid-v4",
  "event_type": "string",
  "timestamp": "ISO-8601 datetime",
  "user_id": "string",
  "data": {
    // Event-specific payload
  },
  "metadata": {
    "source_service": "string",
    "correlation_id": "string (optional)",
    "schema_version": "1.0"
  }
}
```

## Event Types

### 1. task.created

**Topic**: `task-events`
**Producer**: Chat API (MCP tools)
**Consumers**: Recurring Task Service, Audit Service

**Payload**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Client presentation",
    "description": "Prepare slides for Q1 review",
    "priority": "high",
    "tags": ["work", "urgent"],
    "due_at": "2026-02-15T14:00:00Z",
    "reminder_minutes_before": 60,
    "recurrence": "none",
    "recurrence_end_date": null,
    "completed": false
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "conv_abc123",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the newly created task
- `title`: Task title (max 500 chars)
- `description`: Optional detailed description
- `priority`: One of: "high", "medium", "low"
- `tags`: Array of custom labels (0-10 tags, each max 50 chars)
- `due_at`: ISO-8601 datetime or null
- `reminder_minutes_before`: Minutes before due_at to send reminder (1-10080)
- `recurrence`: One of: "none", "daily", "weekly", "monthly", "yearly"
- `recurrence_end_date`: ISO-8601 datetime or null
- `completed`: Always false for newly created tasks

---

### 2. task.updated

**Topic**: `task-events`
**Producer**: Chat API (MCP tools)
**Consumers**: Recurring Task Service, Audit Service

**Payload**:
```json
{
  "event_id": "660e8400-e29b-41d4-a716-446655440001",
  "event_type": "task.updated",
  "timestamp": "2026-02-10T15:00:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "changes": {
      "priority": {
        "old": "medium",
        "new": "high"
      },
      "tags": {
        "old": ["work"],
        "new": ["work", "urgent"]
      }
    },
    "updated_fields": ["priority", "tags"]
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "conv_abc123",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the updated task
- `changes`: Object containing old and new values for each changed field
- `updated_fields`: Array of field names that were modified

---

### 3. task.completed

**Topic**: `task-events`
**Producer**: Chat API (MCP tools)
**Consumers**: Recurring Task Service, Audit Service

**Payload**:
```json
{
  "event_id": "770e8400-e29b-41d4-a716-446655440002",
  "event_type": "task.completed",
  "timestamp": "2026-02-10T16:00:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Weekly team standup",
    "priority": "medium",
    "tags": ["work", "meeting"],
    "recurrence": "weekly",
    "recurrence_end_date": "2026-12-31T23:59:59Z",
    "due_at": "2026-02-10T10:00:00Z",
    "completed_at": "2026-02-10T16:00:00Z"
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "conv_abc123",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the completed task
- `title`: Task title (for recurring task creation)
- `priority`: Task priority (inherited by next occurrence)
- `tags`: Task tags (inherited by next occurrence)
- `recurrence`: Recurrence pattern (used to calculate next occurrence)
- `recurrence_end_date`: When to stop creating recurring tasks
- `due_at`: Original due date (used to calculate next occurrence)
- `completed_at`: When the task was marked complete

**Consumer Behavior** (Recurring Task Service):
- If `recurrence != "none"`, calculate next occurrence date
- Create new task with same title, description, priority, tags, reminder_minutes_before, recurrence
- Set new `due_at` based on recurrence pattern
- Publish `task.created` event for next occurrence

---

### 4. task.deleted

**Topic**: `task-events`
**Producer**: Chat API (MCP tools)
**Consumers**: Audit Service

**Payload**:
```json
{
  "event_id": "880e8400-e29b-41d4-a716-446655440003",
  "event_type": "task.deleted",
  "timestamp": "2026-02-10T17:00:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Obsolete task",
    "deleted_at": "2026-02-10T17:00:00Z"
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "conv_abc123",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the deleted task
- `title`: Task title (for audit trail)
- `deleted_at`: When the task was deleted

---

### 5. reminder.scheduled

**Topic**: `reminders`
**Producer**: Chat API (when task with due_at is created/updated)
**Consumers**: Notification Service

**Payload**:
```json
{
  "event_id": "990e8400-e29b-41d4-a716-446655440004",
  "event_type": "reminder.scheduled",
  "timestamp": "2026-02-10T14:30:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Client presentation",
    "due_at": "2026-02-15T14:00:00Z",
    "reminder_at": "2026-02-15T13:00:00Z",
    "reminder_minutes_before": 60
  },
  "metadata": {
    "source_service": "chat-api",
    "correlation_id": "conv_abc123",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the task
- `title`: Task title (for notification content)
- `due_at`: When the task is due
- `reminder_at`: When to send the reminder (due_at - reminder_minutes_before)
- `reminder_minutes_before`: Minutes before due_at

**Consumer Behavior** (Notification Service):
- Schedule reminder using Dapr Jobs API
- When reminder_at arrives, send notification and publish `reminder.triggered` event

---

### 6. reminder.triggered

**Topic**: `reminders`
**Producer**: Notification Service (via Dapr Jobs API)
**Consumers**: None (terminal event)

**Payload**:
```json
{
  "event_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "event_type": "reminder.triggered",
  "timestamp": "2026-02-15T13:00:00Z",
  "user_id": "user_123",
  "data": {
    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Client presentation",
    "due_at": "2026-02-15T14:00:00Z",
    "notification_sent": true,
    "notification_channel": "email",
    "notification_status": "delivered"
  },
  "metadata": {
    "source_service": "notification-service",
    "correlation_id": "reminder_xyz789",
    "schema_version": "1.0"
  }
}
```

**Field Descriptions**:
- `task_id`: UUID of the task
- `title`: Task title
- `due_at`: When the task is due
- `notification_sent`: Whether notification was successfully sent
- `notification_channel`: Delivery channel (email, push, etc.)
- `notification_status`: Delivery status (delivered, failed, pending)

---

## Event Flow Diagrams

### Task Creation Flow

```
User → Chat API → MCP add_task → Database
                                    ↓
                              task.created event
                                    ↓
                              Kafka (task-events)
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
          Recurring Task Service          Audit Service
          (no action for new tasks)       (log event)
```

### Recurring Task Completion Flow

```
User → Chat API → MCP complete_task → Database (mark complete)
                                           ↓
                                   task.completed event
                                           ↓
                                   Kafka (task-events)
                                           ↓
                              Recurring Task Service
                                           ↓
                              Calculate next occurrence
                                           ↓
                              Create new task (Database)
                                           ↓
                                   task.created event
                                           ↓
                                   Kafka (task-events)
```

### Reminder Scheduling Flow

```
User → Chat API → MCP add_task (with due_at) → Database
                                                   ↓
                                          reminder.scheduled event
                                                   ↓
                                          Kafka (reminders)
                                                   ↓
                                          Notification Service
                                                   ↓
                                    Schedule job via Dapr Jobs API
                                                   ↓
                                    [Wait until reminder_at]
                                                   ↓
                                    Send notification (email/push)
                                                   ↓
                                    Update task.reminder_sent = true
                                                   ↓
                                          reminder.triggered event
                                                   ↓
                                          Kafka (reminders)
```

## Event Ordering Guarantees

**Within a single user's task stream**:
- Events are ordered by timestamp
- Kafka partition key = user_id ensures ordering within partition
- Consumer processes events in order for each user

**Across users**:
- No ordering guarantee (events may be processed in parallel)

## Event Retention

- **task-events**: 7 days
- **reminders**: 7 days

After retention period, events are automatically deleted by Kafka.

## Error Handling

**Event Publishing Failures**:
- Retry up to 3 times with exponential backoff
- If all retries fail, log error and continue (at-least-once delivery not guaranteed for failures)

**Event Consumption Failures**:
- Consumer commits offset only after successful processing
- Failed events are retried automatically
- After 5 failures, event is moved to dead-letter queue (DLQ)

## Schema Evolution

**Adding Fields** (backward-compatible):
- Add new optional fields to `data` object
- Increment `schema_version` to "1.1"
- Old consumers ignore unknown fields

**Removing Fields** (breaking change):
- Requires new event type (e.g., `task.created.v2`)
- Increment `schema_version` to "2.0"
- Maintain both versions during transition period

**Changing Field Types** (breaking change):
- Requires new event type
- Increment `schema_version` to "2.0"

## Testing

**Event Publishing Tests**:
```python
def test_task_created_event():
    task = create_task(user_id="user_123", title="Test task")
    event = get_published_event("task-events")

    assert event["event_type"] == "task.created"
    assert event["user_id"] == "user_123"
    assert event["data"]["task_id"] == task.id
    assert event["data"]["title"] == "Test task"
    assert event["metadata"]["schema_version"] == "1.0"
```

**Event Consumption Tests**:
```python
def test_recurring_task_service_creates_next_occurrence():
    # Publish task.completed event for recurring task
    publish_event("task-events", {
        "event_type": "task.completed",
        "user_id": "user_123",
        "data": {
            "task_id": "task_abc",
            "recurrence": "weekly",
            "due_at": "2026-02-10T10:00:00Z"
        }
    })

    # Wait for consumer to process
    time.sleep(2)

    # Verify next occurrence was created
    next_task = get_task_by_title("Weekly team standup")
    assert next_task.due_at == "2026-02-17T10:00:00Z"
    assert next_task.completed == False
```

## Summary

Phase V defines 6 event types across 2 Kafka topics:
- **task-events**: task.created, task.updated, task.completed, task.deleted
- **reminders**: reminder.scheduled, reminder.triggered

All events follow standardized schema with event_id, event_type, timestamp, user_id, data, and metadata fields. Schema versioning enables future evolution while maintaining backward compatibility.
