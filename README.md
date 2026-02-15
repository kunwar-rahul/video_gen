# Text-to-Video Generation Service

A scalable, modular text-to-video service that converts text prompts into videos by combining Pexels stock footage, AI-generated audio, and FFmpeg rendering.

## Features

✅ **MVP Implementation** - Core pipeline fully functional
- Text-to-video generation from prompts
- Stock footage retrieval from Pexels
- Text-to-speech audio generation
- Automatic subtitle generation
- Video composition with FFmpeg
- REST/MCP API for job submission
- Webhook callbacks for completion
- Job status tracking and progress monitoring
- Docker containerization with optional GPU support
- Redis caching and MinIO object storage

🚀 **Roadmap** - Planned Features
- GPU-accelerated Whisper worker
- Interactive storyboard editor
- Style transfer and visual effects
- Multi-language narration support
- Advanced scene composition with transitions
- Kubernetes deployment manifests
- Billing and quota management
- Enterprise features (watermarking, asset attribution)

## Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add PEXELS_API_KEY

# 2. Start services
docker-compose up --build

# 3. Generate a video
curl -X POST http://localhost:8080/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A calm sunset over a city",
    "duration_target": 60,
    "style": "cinematic"
  }'

# 4. Check status
curl http://localhost:8080/mcp/status/{job_id}

# 5. Get result when ready
curl http://localhost:8080/mcp/result/{job_id}
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client / AI Model                     │
└────────────────────────┬────────────────────────────────┘
                         │
                  REST/MCP API
                         │
        ┌────────────────┴────────────────┐
        │                                 │
    ┌───▼────┐   ┌──────────────────┐   ┌─▼────────┐
    │ Orchest├──→│  Scene Planner   │   │ Job Mgmt │
    │rator   │   └──────────────────┘   └──────────┘
    └───┬────┘
        │
   ┌────┴──────┬─────────┬──────────┐
   │            │         │          │
┌──▼──┐ ┌──────▼──┐ ┌───▼──┐ ┌──────▼───────┐
│Asset│ │Whisper  │ │      │ │             │
│Ret. │ │TTS/ASR  │ │      │ │   Renderer  │
└─────┘ └─────────┘ │      │ │   (FFmpeg)  │
                     └──────┘ └─────────────┘
   │       │         │        │
   └───────┴─────────┴────────┘
           │
    ┌──────▼─────────┐
    │  Object Store  │
    │    (MinIO)     │
    └────────────────┘
```

**Services:**
- **API Gateway**: REST endpoints and MCP server interface
- **Orchestrator**: Pipeline coordination and state management
- **Retriever**: Pexels API integration for stock footage
- **Whisper Worker**: Audio processing (TTS, transcription, subtitles)
- **Renderer**: FFmpeg-based video composition

**Infrastructure:**
- **Redis**: Job queue and ephemeral cache
- **MinIO**: S3-compatible object storage for videos and clips

## API Reference

### POST /mcp/generate
Create a video generation job.

**Request:**
```json
{
  "prompt": "A calm sunrise over a city, inspirational music, 90 seconds",
  "duration_target": 90,
  "style": "cinematic",
  "voice": "en-US-neutral",
  "language": "en",
  "scene_count": 6,
  "callback_url": "https://example.com/webhook",
  "priority": 5
}
```

**Response:** `202 Accepted`
```json
{
  "job_id": "uuid",
  "status": "accepted",
  "message": "Job queued for processing"
}
```

### GET /mcp/status/{job_id}
Check job progress.

**Response:** `200 OK`
```json
{
  "job_id": "uuid",
  "status": "rendering",
  "overall_progress": 75.5,
  "current_step": "Rendering video...",
  "logs": ["Scene planning completed", ...],
  "scenes_processed": 3,
  "total_scenes": 4
}
```

### GET /mcp/result/{job_id}
Get completed video.

**Response:** `200 OK`
```json
{
  "job_id": "uuid",
  "video_url": "s3://videos/uuid/output.mp4",
  "thumbnail_url": "s3://videos/uuid/thumbnail.jpg",
  "duration": 60
}
```

### POST /mcp/cancel/{job_id}
Cancel a job.

### POST /mcp/prefetch
Pre-warm assets for low-latency generation.

### GET /mcp/storyboard/{job_id}
Get intermediate storyboard with scenes and assets.

## Configuration

See `.env.example` for all configuration options:

**Key Settings:**
- `PEXELS_API_KEY` - Pexels API key (required)
- `WHISPER_MODEL` - Model size (tiny, base, small, medium, large)
- `WHISPER_DEVICE` - Computation device (cpu, cuda)
- `TARGET_RESOLUTION` - Output resolution (default: 1920x1080)
- `FFMPEG_PRESET` - Encoding speed (ultrafast to slow)
- `MAX_CONCURRENT_JOBS` - Parallel job limit
- `JOB_TIMEOUT` - Timeout per job (seconds)

## Development

### Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Services

```bash
# Terminal 1: API
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

### Testing

```bash
pytest tests/ -v
pytest tests/ --cov=app
```

## Performance

**Typical Processing Times** (60-second video on modern hardware):
- Scene Planning: ~1 second
- Asset Retrieval: ~5-10 seconds
- Audio Generation: ~10-20 seconds
- Video Rendering: ~30-60 seconds
- **Total: ~1-2 minutes**

**Optimization Tips:**
1. Use `ultrafast` preset for quick previews
2. Enable GPU for Whisper (`WHISPER_DEVICE=cuda`)
3. Use smaller Whisper model for faster transcription
4. Enable asset caching for repeated prompts
5. Scale horizontally with multiple renderer instances

## Monitoring

**Logs:**
```bash
docker-compose logs -f api
docker-compose logs -f orchestrator
```

**MinIO Console:** http://localhost:9001

**Redis CLI:**
```bash
docker-compose exec redis redis-cli
KEYS "*"
GET storyboard_{job_id}
```

## Deployment

### Docker

```bash
docker build -f Dockerfile.api -t video-gen-api:latest .
docker run -p 8080:8080 video-gen-api:latest
```

### Kubernetes

See `infra/k8s/` for deployment manifests.

### Production Considerations

- [ ] PostgreSQL for persistent job storage
- [ ] Managed S3/GCS for object storage
- [ ] API authentication and rate limiting
- [ ] Monitoring with Prometheus/Grafana
- [ ] Auto-scaling based on queue length
- [ ] Distributed tracing (Jaeger)
- [ ] Backup and disaster recovery

## File Structure

```
/app
  /api             - REST/MCP API server
  /orchestrator    - Pipeline coordinator
  /retriever       - Pexels integration
  /whisper_worker  - Audio processing
  /renderer        - FFmpeg video composition
  /common          - Shared models, config, utils
/infra
  docker-compose.yml
  /k8s            - Kubernetes manifests (future)
/docs
  GETTING_STARTED.md
  ARCHITECTURE.md
  API.md
requirements.txt
Dockerfile.*
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API not responding | Check `docker-compose ps`, restart services |
| Pexels API errors | Verify `PEXELS_API_KEY`, check rate limits |
| FFmpeg not found | FFmpeg is installed in Docker, for local: `apt-get install ffmpeg` |
| Out of memory | Reduce `MAX_CONCURRENT_JOBS` or use smaller Whisper model |
| Slow rendering | Use `ultrafast` preset or parallelize with multiple renderers |

## Roadmap

**Phase 1 - MVP** (Complete)
- Core REST API
- Basic scene planning
- Pexels integration
- Whisper-based audio
- FFmpeg rendering
- Docker compose setup

**Phase 2 - Beta** (Next)
- GPU support
- Better TTS options
- Subtitle rendering
- Job persistence
- Web UI
- Comprehensive testing

**Phase 3 - Production**
- Kubernetes deployment
- Authentication & billing
- Advanced effects
- Enterprise features
- Horizontal scaling

**Phase 4 - Advanced**
- Style transfer
- Interactive editor  
- Plugin marketplace
- Multi-language support
- Asset versioning

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a pull request

## License

MIT License - see LICENSE file.

## Support

- 📖 [Getting Started Guide](docs/GETTING_STARTED.md)
- 🏗️ [Architecture Documentation](docs/ARCHITECTURE.md)
- 🔌 [API Reference](docs/API.md)
- 🐛 [Issue Tracker](https://github.com/your-org/video-gen/issues)

---

Built with ❤️ for creators and AI developers.
