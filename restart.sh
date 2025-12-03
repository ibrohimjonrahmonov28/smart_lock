#!/bin/bash

# SmartLock Backend - Restart Script
# This script restarts all Docker containers

echo "🔄 Restarting SmartLock Backend..."
echo "================================"
echo ""

docker-compose restart

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "================================"
echo "✅ Services restarted!"
echo "================================"
echo ""
