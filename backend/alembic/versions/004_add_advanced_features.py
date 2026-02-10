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
    """Add Phase V fields to tasks table."""
    # Add tags column (array of text)
    op.add_column('tasks', sa.Column('tags', postgresql.ARRAY(sa.Text),
                                      server_default='{}', nullable=False))

    # Add due_at column (rename from due_date if exists, or add new)
    # Note: due_date already exists, so we'll add the new fields only

    # Add reminder_minutes_before column
    op.add_column('tasks', sa.Column('reminder_minutes_before', sa.Integer,
                                      server_default='60', nullable=False))

    # Add recurrence column
    op.add_column('tasks', sa.Column('recurrence', sa.String(20),
                                      server_default='none', nullable=False))

    # Add recurrence_end_date column
    op.add_column('tasks', sa.Column('recurrence_end_date',
                                      sa.TIMESTAMP(timezone=True), nullable=True))

    # Add reminder_sent column
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean,
                                      server_default='false', nullable=False))

    # Update priority column to use Phase V values (high/medium/low instead of High/Medium/Low)
    # This is a data migration - convert existing values
    op.execute("UPDATE tasks SET priority = LOWER(priority)")

    # Add constraints
    op.create_check_constraint(
        'check_priority_phase_v',
        'tasks',
        "priority IN ('high', 'medium', 'low')"
    )
    op.create_check_constraint(
        'check_recurrence',
        'tasks',
        "recurrence IN ('none', 'daily', 'weekly', 'monthly', 'yearly')"
    )

    # Add indexes for new fields
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_recurrence', 'tasks', ['recurrence'],
                    postgresql_where=sa.text("recurrence != 'none'"))


def downgrade():
    """Remove Phase V fields from tasks table."""
    # Drop indexes
    op.drop_index('idx_tasks_recurrence', 'tasks')
    op.drop_index('idx_tasks_tags', 'tasks')

    # Drop constraints
    op.drop_constraint('check_recurrence', 'tasks')
    op.drop_constraint('check_priority_phase_v', 'tasks')

    # Revert priority values to capitalized form
    op.execute("UPDATE tasks SET priority = INITCAP(priority)")

    # Drop columns
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence')
    op.drop_column('tasks', 'reminder_minutes_before')
    op.drop_column('tasks', 'tags')
