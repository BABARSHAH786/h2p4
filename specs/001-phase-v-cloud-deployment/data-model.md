# Phase 1: Data Model - Phase V Advanced Cloud Deployment

**Feature**: Phase V - Advanced Cloud Deployment
**Date**: 2026-02-10
**Status**: Complete

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│─────────────────│
│ id (PK)         │
│ email           │
│ name            │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│   Conversation  │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐
│    Message      │
│─────────────────│
│ id (PK)         │
│ conversation_id │
│ role            │
│ content         │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│      User       │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────────────────────────────────┐
│                    Task                         │
│─────────────────────────────────────────────────│
│ id (PK)                                         │
│ user_id (FK)                                    │
│ title                                           │
│ description                                     │
│ completed                                       │
│ created_at                                      │
│ updated_at                                      │
│ ─────────────────────────────────────────────── │
│ NEW PHASE V FIELDS:                             │
│ priority (high/medium/low)                      │
│ tags (array)                                    │
│ due_at (timestamp)                              │
│ reminder_minutes_before (integer)               │
│ recurrence (none/daily/weekly/monthly/yearly)   │
│ recurrence_end_date (timestamp)                 │
│ reminder_sent (boolean)                         │
└─────────────────────────────────────────────────┘
```

## Database Schema

### Updated `tasks` Table

```sql
CREATE TABLE tasks (
    -- Existing fields (Phase III)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- NEW: Phase V fields
    priority VARCHAR(10) DEFAULT 'medium'
        CHECK (priority IN ('high', 'medium', 'low')),
    tags TEXT[] DEFAULT '{}',
    due_at TIMESTAMP,
    reminder_minutes_before INTEGER DEFAULT 60,
    recurrence VARCHAR(20) DEFAULT 'none'
        CHECK (recurrence IN ('none', 'daily', 'weekly', 'monthly', 'yearly')),
    recurrence_end_date TIMESTAMP,
    reminder_sent BOOLEAN DEFAULT FALSE,

    -- Indexes
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Existing indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);

-- NEW: Phase V indexes
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_at ON tasks(due_at);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_recurrence ON tasks(recurrence) WHERE recurrence != 'none';
```

### Existing Tables (No Changes)

**`users` table** (managed by Better Auth):
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**`conversations` table**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**`messages` table**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

## Entity Definitions

### Task Entity (Updated)

**Purpose**: Represents a todo item with advanced features (priorities, tags, due dates, reminders, recurrence)

**Fields**:
- `id` (UUID): Unique identifier
- `user_id` (string): Owner of the task (FK to users.id)
- `title` (string, max 500 chars): Task title
- `description` (text, optional): Detailed description
- `completed` (boolean): Completion status
- `created_at` (timestamp): Creation time
- `updated_at` (timestamp): Last modification time
- **NEW** `priority` (enum: high/medium/low): Task priority level
- **NEW** `tags` (array of strings): Custom labels for categorization
- **NEW** `due_at` (timestamp, optional): Due date and time
- **NEW** `reminder_minutes_before` (integer, default 60): Minutes before due_at to send reminder
- **NEW** `recurrence` (enum: none/daily/weekly/monthly/yearly): Recurrence pattern
- **NEW** `recurrence_end_date` (timestamp, optional): When to stop creating recurring tasks
- **NEW** `reminder_sent` (boolean, default false): Whether reminder notification was sent

**Validation Rules**:
- `title` is required and non-empty
- `priority` must be one of: high, medium, low
- `tags` array can contain 0-10 tags, each max 50 chars
- `due_at` must be in the future when created
- `reminder_minutes_before` must be positive (1-10080 minutes = 1 week)
- `recurrence_end_date` must be after `due_at` if both are set
- If `recurrence != 'none'`, `due_at` is required

**Business Rules**:
- When a recurring task is completed, a new task is created with:
  - Same title, description, priority, tags, reminder_minutes_before, recurrence
  - New `due_at` calculated based on recurrence pattern
  - `completed = false`
  - `reminder_sent = false`
- When `due_at` is set and `reminder_minutes_before` is specified, a reminder job is scheduled
- When reminder job triggers, `reminder_sent` is set to `true` and notification is sent

### User Entity (Unchanged)

**Purpose**: Represents an authenticated user

**Fields**:
- `id` (string): Unique identifier (managed by Better Auth)
- `email` (string): User's email address
- `name` (string): User's display name
- `created_at` (timestamp): Account creation time

### Conversation Entity (Unchanged)

**Purpose**: Represents a chat session between user and AI agent

**Fields**:
- `id` (UUID): Unique identifier
- `user_id` (string): Owner of the conversation (FK to users.id)
- `created_at` (timestamp): Conversation start time
- `updated_at` (timestamp): Last message time

### Message Entity (Unchanged)

**Purpose**: Represents a single message in a conversation

**Fields**:
- `id` (UUID): Unique identifier
- `conversation_id` (UUID): Parent conversation (FK to conversations.id)
- `role` (enum: user/assistant): Message sender
- `content` (text): Message text
- `created_at` (timestamp): Message time

## Data Access Patterns

### Task Operations

**Create Task**:
```python
task = Task(
    user_id=user_id,
    title=title,
    description=description,
    priority=priority,  # NEW
    tags=tags,  # NEW
    due_at=due_at,  # NEW
    reminder_minutes_before=reminder_minutes_before,  # NEW
    recurrence=recurrence,  # NEW
    recurrence_end_date=recurrence_end_date  # NEW
)
session.add(task)
session.commit()

# Publish event
publish_event("task.created", task)

# Schedule reminder if due_at is set
if task.due_at:
    schedule_reminder(task)
```

**List Tasks with Filters**:
```python
query = session.query(Task).filter(Task.user_id == user_id)

# Filter by status
if status == "completed":
    query = query.filter(Task.completed == True)
elif status == "pending":
    query = query.filter(Task.completed == False)

# NEW: Filter by priority
if priority:
    query = query.filter(Task.priority == priority)

# NEW: Filter by tags
if tags:
    query = query.filter(Task.tags.overlap(tags))

# NEW: Filter by due date range
if due_after:
    query = query.filter(Task.due_at >= due_after)
if due_before:
    query = query.filter(Task.due_at <= due_before)

# NEW: Sort
if order_by == "due_date":
    query = query.order_by(Task.due_at.asc())
elif order_by == "priority":
    query = query.order_by(
        case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3)
        )
    )
else:
    query = query.order_by(Task.created_at.desc())

tasks = query.all()
```

**Search Tasks**:
```python
# NEW: Keyword search
query = session.query(Task).filter(
    Task.user_id == user_id,
    or_(
        Task.title.ilike(f"%{keyword}%"),
        Task.description.ilike(f"%{keyword}%")
    )
)
tasks = query.all()
```

**Complete Recurring Task**:
```python
# Mark current task as completed
task.completed = True
task.updated_at = datetime.utcnow()
session.commit()

# Publish event
publish_event("task.completed", task)

# Recurring Task Service will consume this event and create next occurrence
```

## Migration Strategy

### Alembic Migration: `004_add_advanced_features.py`

```python
"""Add Phase V advanced features

Revision ID: 004
Revises: 003
Create Date: 2026-02-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('tasks', sa.Column('priority', sa.String(10),
                                      server_default='medium', nullable=False))
    op.add_column('tasks', sa.Column('tags', postgresql.ARRAY(sa.Text),
                                      server_default='{}', nullable=False))
    op.add_column('tasks', sa.Column('due_at', sa.TIMESTAMP, nullable=True))
    op.add_column('tasks', sa.Column('reminder_minutes_before', sa.Integer,
                                      server_default='60', nullable=False))
    op.add_column('tasks', sa.Column('recurrence', sa.String(20),
                                      server_default='none', nullable=False))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.TIMESTAMP, nullable=True))
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean,
                                      server_default='false', nullable=False))

    # Add constraints
    op.create_check_constraint(
        'check_priority',
        'tasks',
        "priority IN ('high', 'medium', 'low')"
    )
    op.create_check_constraint(
        'check_recurrence',
        'tasks',
        "recurrence IN ('none', 'daily', 'weekly', 'monthly', 'yearly')"
    )

    # Add indexes
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_at', 'tasks', ['due_at'])
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_recurrence', 'tasks', ['recurrence'],
                    postgresql_where=sa.text("recurrence != 'none'"))


def downgrade():
    # Drop indexes
    op.drop_index('idx_tasks_recurrence', 'tasks')
    op.drop_index('idx_tasks_tags', 'tasks')
    op.drop_index('idx_tasks_due_at', 'tasks')
    op.drop_index('idx_tasks_priority', 'tasks')

    # Drop constraints
    op.drop_constraint('check_recurrence', 'tasks')
    op.drop_constraint('check_priority', 'tasks')

    # Drop columns
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'reminder_minutes_before')
    op.drop_column('tasks', 'due_at')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
```

### Migration Execution

**Local Development**:
```bash
cd backend
alembic upgrade head
```

**Production (via CI/CD)**:
```bash
# Run migration before deploying new code
kubectl exec -it deployment/chat-api -n todo-app -- alembic upgrade head
```

## Data Validation

### SQLModel Schema

```python
from sqlmodel import Field, SQLModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Recurrence(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[str] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # NEW: Phase V fields
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: List[str] = Field(default_factory=list, sa_column_kwargs={"type_": postgresql.ARRAY(sa.Text)})
    due_at: Optional[datetime] = None
    reminder_minutes_before: int = Field(default=60, ge=1, le=10080)
    recurrence: Recurrence = Field(default=Recurrence.NONE)
    recurrence_end_date: Optional[datetime] = None
    reminder_sent: bool = Field(default=False)
```

## Performance Considerations

### Index Usage

**Priority Filter**:
```sql
-- Uses idx_tasks_priority
SELECT * FROM tasks WHERE user_id = ? AND priority = 'high';
```

**Tag Filter**:
```sql
-- Uses idx_tasks_tags (GIN index)
SELECT * FROM tasks WHERE user_id = ? AND tags && ARRAY['work', 'urgent'];
```

**Due Date Range**:
```sql
-- Uses idx_tasks_due_at
SELECT * FROM tasks WHERE user_id = ? AND due_at BETWEEN ? AND ?;
```

**Recurring Tasks**:
```sql
-- Uses idx_tasks_recurrence (partial index)
SELECT * FROM tasks WHERE recurrence != 'none' AND completed = true;
```

### Query Optimization

**Estimated Query Times** (for 1000 tasks per user):
- List all tasks: <10ms
- Filter by priority: <5ms
- Filter by tags: <20ms (GIN index)
- Search by keyword: <50ms (full-text search)
- Sort by due date: <15ms

## Data Integrity

### Constraints

1. **Priority Constraint**: Ensures priority is one of: high, medium, low
2. **Recurrence Constraint**: Ensures recurrence is one of: none, daily, weekly, monthly, yearly
3. **Foreign Key Constraint**: Ensures user_id references valid user
4. **Check Constraint**: Ensures reminder_minutes_before is positive

### Validation Logic

```python
def validate_task(task: Task):
    # Title is required
    if not task.title or not task.title.strip():
        raise ValueError("Title is required")

    # Tags validation
    if len(task.tags) > 10:
        raise ValueError("Maximum 10 tags allowed")
    for tag in task.tags:
        if len(tag) > 50:
            raise ValueError("Tag length must be <= 50 characters")

    # Due date validation
    if task.due_at and task.due_at < datetime.utcnow():
        raise ValueError("Due date must be in the future")

    # Recurrence validation
    if task.recurrence != Recurrence.NONE and not task.due_at:
        raise ValueError("Recurring tasks must have a due date")

    # Recurrence end date validation
    if task.recurrence_end_date and task.due_at:
        if task.recurrence_end_date <= task.due_at:
            raise ValueError("Recurrence end date must be after due date")
```

## Summary

Phase V adds 7 new fields to the `tasks` table to support advanced features:
- **priority**: Task prioritization (high/medium/low)
- **tags**: Custom categorization labels
- **due_at**: Due date and time
- **reminder_minutes_before**: Reminder scheduling
- **recurrence**: Recurring task pattern
- **recurrence_end_date**: When to stop recurring
- **reminder_sent**: Notification delivery tracking

All changes are backward-compatible with existing data (default values provided). Migration can be rolled back if needed.
