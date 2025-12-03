#!/bin/bash

# SmartLock Backend - View Logs
# This script shows logs from all services

SERVICE=${1:-web}

echo "📋 Viewing logs for: $SERVICE"
echo "================================"
echo ""
echo "💡 Press Ctrl+C to exit"
echo ""

docker-compose logs -f $SERVICE
