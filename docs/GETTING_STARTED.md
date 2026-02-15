# Text-to-Video Generation Service - Getting Started Guide

Welcome! This is an implementation of the text-to-video generation service design specification. This MVP includes the core pipeline for converting text prompts into videos by combining Pexels stock footage, audio generation, and FFmpeg rendering.

## Architecture Overview

The service consists of 5 microservices:

1. **API Server** - REST/MCP endpoints for job submission and status tracking
2. **Orchestrator** - Coordinates the pipeline, plans scenes, and manages job state
3. **Retriever** - Fetches stock footage from Pexels based on scene descriptions
4. **Whisper Worker** - Generates speech audio (TTS) and processes transcriptions
5. **Renderer** - Composes video using FFmpeg

All services communicate through a Redis cache and MinIO object storage.

## Prerequisites

- **Docker** and **Docker Compose** (version 3.8+)
- **Python 3.11+** (for local development)
- **Pexels API Key** (sign up at https://www.pexels.com/api/)
- **FFmpeg** (installed automatically in Docker)

## Quick Start

### 1. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env and add your PEXELS_API_KEY
```

### 2. Start Services with Docker Compose

```bash
docker-compose up --build
```

This will start:
- API server on `http://localhost:8080`
- MinIO on `http://localhost:9000` (username: minioadmin, password: minioadmin)
- Redis on `http://localhost:6379`
- All microservices

### 3. Submit Your First Job

```bash
curl -X POST http://localhost:8080/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over the ocean with waves crashing on the beach",
    "duration_target": 60,
    "style": "cinematic",
    "voice": "en-US-neutral",
    "callback_url": "https://your-webhook-endpoint.com/callback"
  }'
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "accepted",
  "message": "Job queued for processing"
}
```

### 4. Check Job Status

```bash
curl http://localhost:8080/mcp/status/{job_id}
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "rendering",
  "overall_progress": 75.5,
  "current_step": "Rendering video...",
  "scenes_processed": 3,
  "total_scenes": 4
}
```

### 5. Get Results

Once status is "completed":

```bash
curl http://localhost:8080/mcp/result/{job_id}
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "video_url": "s3://videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/output.mp4",
  "thumbnail_url": "s3://videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/thumbnail.jpg"
}
```

## API Endpoints

### Generate Video
- **POST** `/mcp/generate`
- Creates a new video generation job
- Returns: `job_id`, `status`

### Check Status
- **GET** `/mcp/status/<job_id>`
- Returns: `status`, `progress`, `current_step`, `logs`

### Get Results
- **GET** `/mcp/result/<job_id>`
- Returns: `video_url`, `thumbnail_url` (when completed)

### Cancel Job
- **POST** `/mcp/cancel/<job_id>`
- Stops an in-progress job

### Prefetch Assets
- **POST** `/mcp/prefetch`
- Pre-caches assets for faster rendering later

### Get Storyboard
- **GET** `/mcp/storyboard/<job_id>`
- Returns intermediate storyboard with scenes and assets

## Local Development (Without Docker)

### Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Whisper separately (if using GPU)
pip install openai-whisper torch torchaudio  # GPU version
```

### Run Services Individually

```bash
# Terminal 1: API Server
python -m api.main

# Terminal 2: Orchestrator 
python -m orchestrator.main

# Terminal 3: Retriever
python -m retriever.main

# Terminal 4: Whisper Worker
python -m whisper_worker.main

# Terminal 5: Renderer
python -m renderer.main
```

You'll also need Redis and MinIO running (or update config to use cloud services).

## Configuration

Edit `.env` to customize:

- **Pexels API**: `PEXELS_API_KEY`
- **FFmpeg Quality**: `FFMPEG_PRESET` (ultrafast, fast, medium, slow)
- **Resolution**: `TARGET_RESOLUTION` (e.g., 1920x1080)
- **Whisper Model**: `WHISPER_MODEL` (tiny, base, small, medium, large)
- **Job Timeout**: `JOB_TIMEOUT` (seconds)
- **Webhooks**: `ENABLE_WEBHOOKS` (true/false)

## Monitoring

### View Logs

```bash
# Watch API logs
docker-compose logs -f api

# Watch all services
docker-compose logs -f
```

### MinIO Console

Visit `http://localhost:9001` to browse stored videos and assets.

### Redis CLI

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View job cache
SCAN 0
GET storyboard_{job_id}
```

## Architecture Details

### Request Flow

1. **Client** → POST `/mcp/generate` with prompt
2. **API** → Creates job, stores in Redis
3. **Orchestrator** → Fetches job, plans scenes
4. **Retriever** → Searches Pexels for clips
5. **Whisper** → Generates TTS audio
6. **Renderer** → Composes video with FFmpeg
7. **API** → Returns result or triggers webhook

### Data Storage

- **Job metadata**: Redis (fast access)
- **Video clips**: MinIO (object storage)
- **Generated videos**: MinIO (final output)
- **Cache**: In-memory with TTL

## Performance Tips

1. **GPU Rendering**: Update `Dockerfile.whisper` and `Dockerfile.renderer` to use CUDA:
   ```dockerfile
   FROM nvidia/cuda:12.2-runtime-ubuntu22.04
   ```

2. **Quality/Speed Trade-off**:
   - Low quality: `ultrafast`, 1280x720, faster rendering
   - High quality: `slow`, 3840x2160, slower but better

3. **Caching**: Enable asset and job caching to skip redundant work:
   ```
   ASSET_CACHE_ENABLED=true
   JOB_CACHE_TTL=86400
   ```

4. **Parallel Processing**: Increase `MAX_CONCURRENT_JOBS` if you have more resources

## Troubleshooting

### "Cannot connect to Minio"
```bash
# Check MinIO is running
docker-compose ps minio

# Restart MinIO
docker-compose restart minio
```

### "FFmpeg command not found"
```bash
# Install FFmpeg in container
docker-compose exec renderer apt-get update && apt-get install -y ffmpeg
```

### "Pexels API error"
- Verify `PEXELS_API_KEY` in `.env`
- Check API key has video access
- Check rate limits (Pexels free tier: 200 req/hour)

### "Job stuck in PENDING"
```bash
# Check orchestrator is running
docker-compose logs orchestrator

# Restart orchestrator
docker-compose restart orchestrator
```

## Next Steps

### Improve the MVP

1. **Persistent Job Storage**: Replace Redis cache with PostgreSQL
2. **Real Asset Retrieval**: Implement actual Pexels download
3. **Subtitle Rendering**: Add burnt-in subtitles to video
4. **Error Handling**: Implement retry logic with exponential backoff
5. **Authentication**: Add API key validation
6. **Metrics**: Add Prometheus metrics for monitoring

### Advanced Features

1. **Style Transfer**: Apply AI-driven visual filters
2. **Interactive Editor**: Build web UI for clip selection
3. **Multi-language**: Support TTS in multiple languages
4. **Versioning**: Keep timeline edit history
5. **Webhooks**: Proper async webhook delivery
6. **Cost Tracking**: Monitor Pexels API usage and costs

## Testing

```bash
# Run tests
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=app --cov-report=html

# Run linter
pylint app/
```

## Deployment

### Kubernetes

```bash
# Build images
docker build -f Dockerfile.api -t video-gen-api:latest .
docker build -f Dockerfile.orchestrator -t video-gen-orchestrator:latest .
# ... build other images

# Push to registry
docker tag video-gen-api:latest myregistry.azurecr.io/video-gen-api:latest
docker push myregistry.azurecr.io/video-gen-api:latest
# ... push other images

# Deploy with kubectl
kubectl apply -f infra/k8s/
```

### Production Checklist

- [ ] Set up proper PostgreSQL/MongoDB for job persistence
- [ ] Configure managed object storage (GCS, S3, Azure Blob)
- [ ] Enable authentication and rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure auto-scaling based on job queue length
- [ ] Implement proper error recovery and retries
- [ ] Set up CI/CD pipeline
- [ ] Review and implement security best practices
- [ ] Conduct load testing
- [ ] Plan disaster recovery

## Support and Contributing

For issues, questions, or contributions, please:

1. Check existing issues
2. Review logs and error messages
3. Follow bug report template
4. Include reproduction steps

## License

See LICENSE file for details.
