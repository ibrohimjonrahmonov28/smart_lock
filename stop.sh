#!/bin/bash

# SmartLock Backend - Stop Script
# This script stops all Docker containers

echo "🛑 Stopping SmartLock Backend..."
echo "================================"
echo ""

docker-compose down

echo ""
echo "================================"
echo "✅ All services stopped!"
echo "================================"
echo ""
echo "💡 To start again, run: ./start.sh"
echo ""
