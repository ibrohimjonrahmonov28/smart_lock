#!/bin/bash
set -e

echo "🚀 Starting SmartLock Backend..."

# Wait for database
echo "⏳ Waiting for database..."
python manage.py wait_for_db

# Run migrations
echo "📊 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
mkdir -p /app/logs

echo "✅ Initialization complete!"

# Execute the main command
exec "$@"