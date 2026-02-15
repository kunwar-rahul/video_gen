#!/bin/bash
# Quick start script for the video generation service

set -e

echo "🎬 Text-to-Video Generation Service - Quick Start"
echo "=================================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Setup .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your PEXELS_API_KEY"
    echo "   Then run this script again."
    exit 0
fi

# Extract PEXELS_API_KEY
PEXELS_KEY=$(grep "^PEXELS_API_KEY=" .env | cut -d'=' -f2)

if [ -z "$PEXELS_KEY" ] || [ "$PEXELS_KEY" = "your_pexels_api_key_here" ]; then
    echo "❌ PEXELS_API_KEY not configured in .env"
    echo "   Please edit .env and add your Pexels API key from https://www.pexels.com/api/"
    exit 1
fi

echo "✅ Configuration looks good"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check health
echo ""
echo "🏥 Checking service health..."

for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ API is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API did not become healthy in time"
        echo "   Check logs with: docker-compose logs -f api"
        exit 1
    fi
    echo "   Attempt $i/30..."
    sleep 1
done

echo ""
echo "✅ All services are running!"
echo ""
echo "📍 Available services:"
echo "   API Server:     http://localhost:8080"
echo "   MinIO Console:  http://localhost:9001"
echo "   Redis:          localhost:6379"
echo ""
echo "🎯 Quick test:"
echo ""
echo "   # Generate a video"
echo "   curl -X POST http://localhost:8080/mcp/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"prompt\": \"A sunset over the ocean\", \"duration_target\": 30}'"
echo ""
echo "   # Check status"
echo "   curl http://localhost:8080/mcp/status/{job_id}"
echo ""
echo "📚 Documentation:"
echo "   • Getting Started: docs/GETTING_STARTED.md"
echo "   • Architecture:    docs/ARCHITECTURE.md"
echo "   • README:          README.md"
echo ""
echo "📖 View logs:"
echo "   docker-compose logs -f api"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
