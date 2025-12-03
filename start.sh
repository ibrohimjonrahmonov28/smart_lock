#!/bin/bash

# SmartLock Backend - Start Script
# This script starts all Docker containers for the SmartLock backend

set -e

echo "🚀 Starting SmartLock Backend..."
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and update the passwords!"
        echo "Then run this script again."
        exit 0
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
fi

echo "📦 Building Docker images..."
docker-compose build --no-cache

echo ""
echo "🔄 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "================================"
echo "✅ SmartLock Backend Started!"
echo "================================"
echo ""
echo "📍 Access Points:"
echo "  • API:          http://localhost:8000/api/"
echo "  • API Docs:     http://localhost:8000/api/docs/"
echo "  • Admin Panel:  http://localhost:8000/admin/"
echo "  • Health Check: http://localhost:8000/health/"
echo ""
echo "📊 Database:"
echo "  • PostgreSQL:   localhost:5432"
echo "  • Redis:        localhost:6379"
echo ""
echo "📚 Useful Commands:"
echo "  • View logs:    docker-compose logs -f web"
echo "  • Stop all:     ./stop.sh"
echo "  • Restart:      ./restart.sh"
echo "  • Shell access: docker-compose exec web bash"
echo ""
echo "💡 Default Admin Credentials:"
echo "  • Email:    admin@smartlock.com"
echo "  • Password: admin123"
echo "  (Created automatically on first run)"
echo ""
