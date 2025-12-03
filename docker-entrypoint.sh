#!/bin/bash
set -e

echo "🚀 Starting SmartLock Backend..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Run migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "👤 Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@smartlock.com').exists():
    user = User.objects.create_superuser(
        email='admin@smartlock.com',
        password='admin',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created: admin@smartlock.com / admin')
else:
    print('ℹ️  Superuser already exists')
" || true

# Create logs directory
mkdir -p /app/logs

echo "✅ Initialization complete!"
echo "🚀 Starting application..."

# Execute the main command
exec "$@"