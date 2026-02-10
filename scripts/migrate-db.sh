#!/bin/bash
# Run database migration

set -e

echo "🗄️ Running database migration..."

cd backend

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable is not set"
    exit 1
fi

# Install dependencies if needed
if ! command -v alembic &> /dev/null; then
    echo "Installing dependencies..."
    pip install uv
    uv pip install --system -r pyproject.toml
fi

# Run migration
echo "Running alembic upgrade head..."
alembic upgrade head

echo "✅ Migration completed successfully!"
