# System Architecture

## Overview

The text-to-video generation service is built as a distributed, modular system with clear separation of concerns. Each component is independently deployable and scalable.

## Component Architecture

### API Gateway / REST Server
**File**: `app/api/main.py`

**Responsibilities:**
- Expose REST endpoints (`/mcp/generate`, `/mcp/status`, `/mcp/result`, etc.)
- Validate incoming requests
- Maintain job registry
- Return appropriate HTTP status codes
- Support webhook callbacks

**Dependencies:**
- Flask (HTTP framework)
- Redis (job metadata storage)
- Orchestrator (job processing)

**API Specification:**
- `/health` - Health check
- `/mcp/generate` - Create video job
- `/mcp/status/<job_id>` - Get progress
- `/mcp/result/<job_id>` - Get final video
- `/mcp/cancel/<job_id>` - Cancel job
- `/mcp/prefetch` - Pre-warm assets
- `/mcp/storyboard/<job_id>` - Get intermediate storyboard

### Orchestrator Service
**File**: `app/orchestrator/main.py`

**Responsibilities:**
- Coordinate the entire video generation pipeline
- Scene planning (split prompt into scenes)
- Asset retrieval coordination
- Audio/subtitle generation
- Webhook triggering
- Error handling and retry logic
- Progress tracking

**Key Classes:**
- `ScenePlanner` - NLP-based scene splitting
- `JobOrchestrator` - Main pipeline coordinator

**Pipeline Stages:**
1. Scene Planning (20% progress)
2. Asset Retrieval (40% progress)
3. Audio Generation (60% progress)
4. Video Rendering (100% progress)

### Asset Retriever Service
**File**: `app/retriever/main.py`

**Responsibilities:**
- Query Pexels API for video clips
- Select best matching clips per scene
- Download and cache assets
- Manage Pexels API rate limits
- Generate search queries from scene descriptions

**Key Classes:**
- `PexelsRetriever` - Pexels API client
- `RetrieverService` - Service interface

**Algorithm:**
- Extract keywords from scene description
- Determine shot type (close-up, aerial, slow-motion, etc.)
- Search Pexels with expanded queries
- Pick clip with duration closest to target

### Whisper Worker Service
**File**: `app/whisper_worker/main.py`

**Responsibilities:**
- Text-to-speech (TTS) audio generation
- Audio transcription and language detection
- Subtitle generation with timing
- Word-level alignment

**Key Classes:**
- `WhisperProcessor` - Whisper model wrapper
- `TTSProcessor` - Speech synthesis
- `WhisperWorkerService` - Service coordinator

**TTS Options:**
- gTTS (Google Text-to-Speech) - Free, good quality
- Azure Cognitive Services - High quality (optional)
- AWS Polly - Professional (optional)

**Subtitle Generation:**
- Estimate timing based on text length
- Split into chunks for readability
- Create VTT format with millisecond precision

### Renderer Service
**File**: `app/renderer/main.py`

**Responsibilities:**
- Compose video timeline
- Apply transitions and effects
- Render final MP4 video
- Extract thumbnails
- Handle various quality presets

**Key Classes:**
- `FFmpegRenderer` - FFmpeg wrapper
- `RendererService` - Service coordinator

**Quality Presets:**
- **Low**: 1280x720, ultrafast encoding (2-3x realtime)
- **Medium**: 1920x1080, medium encoding (1-2x realtime)
- **High**: 3840x2160, slow encoding (0.5-1x realtime)

**FFmpeg Pipeline:**
```
Input Clips → Concat → Scale → Transitions → Subtitles → Encode → Output
```

## Data Models

### Core Models
**File**: `app/common/models.py`

- `VideoRequest` - Incoming request with parameters
- `Scene` - Individual video scene (description, duration, keywords, clip)
- `Storyboard` - Complete pipeline with all scenes and audio
- `JobProgress` - Current job status and progress
- `JobStatus` - Enum of job states (pending, rendering, completed, failed)
- `PexelsClip` - Stock video from Pexels
- `AudioSegment` - Audio track with timing
- `Subtitle` - Subtitle entry with timing

### Data Flow

```
VideoRequest
    ↓
JobOrchestrator.orchestrate_job()
    ├→ ScenePlanner.plan_scenes() → Scene[]
    ├→ PexelsRetriever.get_best_clip() → PexelsClip[]
    ├→ TTSProcessor.generate_speech() → Audio file
    ├→ WhisperProcessor.transcribe_audio() → AudioSegment[], Subtitle[]
    ├→ Storyboard (cached in Redis)
    └→ FFmpegRenderer.render_video() → MP4 file

Result cached and returned to client
```

## Data Storage

### Redis Cache
**Purpose**: Fast access to job metadata and intermediate results

**Keys:**
- `storyboard_{job_id}` - Complete storyboard JSON
- `assets_{job_id}` - Retrieved clips mapping
- `result_{job_id}` - Final video result

**TTL**: 24 hours (configurable)

### MinIO Object Storage
**Purpose**: Durable storage for videos and assets

**Buckets:**
- `video-assets` - Stock clips downloaded from Pexels
- `generated-videos` - Final output videos
- `audio` - Generated audio files
- `thumbnails` - Video thumbnails

**S3-compatible API** - Can be replaced with AWS S3, GCS, Azure Blob Storage

## Communication Patterns

### Synchronous (Direct Service Calls)
- API → Orchestrator: Job submission
- Orchestrator → Retriever: Asset search
- Orchestrator → Whisper: Audio generation
- Orchestrator → Renderer: Video composition

### Asynchronous (Webhooks)
- Orchestrator → Callback URL: Job completion notification
- Format: `POST` with JSON result

### Caching
- All intermediate results cached in Redis
- Enables resumable processing and progress tracking
- Shared across service instances

## Job State Machine

```
         ┌─────────┐
         │ PENDING │
         └────┬────┘
              │
       ┌──────▼──────────┐
       │ SCENE_PLANNING  │
       └──────┬──────────┘
              │
       ┌──────▼──────────────┐
       │ ASSET_RETRIEVAL     │
       └──────┬──────────────┘
              │
       ┌──────▼──────────────┐
       │ TTS_GENERATION      │
       └──────┬──────────────┘
              │
       ┌──────▼──────────────┐
       │ AUDIO_PROCESSING    │
       └──────┬──────────────┘
              │
       ┌──────▼──────────────┐
       │ RENDERING           │
       └──────┬──────────────┘
              │
       ┌──────▼──────────┐
       │ COMPLETED       │
       └────────────────┘
              ▲
              │ or ├─ FAILED ─┐
              │                │
         CANCELLED ◄──┬────────┘

(Any state can transition to CANCELLED or FAILED)
```

## Error Handling

### Retry Logic
- Max retries: 3
- Exponential backoff starting at 5 seconds
- Implemented at orchestrator level

### Fallbacks
- **No Pexels clips found**: Use solid color frame
- **TTS failure**: Continue with text-only subtitles
- **Whisper unavailable**: Use dummy timestamps
- **FFmpeg failure**: Return error, trigger webhook with error

## Scaling Patterns

### Horizontal Scaling
- Run multiple API server instances behind load balancer
- Run multiple orchestrator instances with shared Redis queue
- Run multiple renderer instances for parallel video encoding

### Resource Optimization
- Scene planning: CPU-bound (parallelizable)
- Asset retrieval: I/O-bound (network calls to Pexels)
- Audio generation: Memory-bound (Whisper model)
- Video rendering: CPU/GPU-intensive (FFmpeg)

### Queue Management
- Redis as primary queue
- Future: Move to RabbitMQ or Celery for reliability
- Monitor queue depth, implement auto-scaling triggers

## Monitoring and Observability

### Metrics
- Job count (by status)
- Average rendering time
- Pexels API calls/minute
- Video cache hit ratio
- Service latency percentiles

### Logging
- Structured JSON logs
- Trace job_id across services
- Log level configurable per service

### Health Checks
- `/health` endpoint on API
- Service readiness via Redis connectivity
- FFmpeg availability check at startup

## Security Considerations

### Current MVP
- No authentication (for development)
- Public API endpoints

### Production Requirements
- API key authentication
- Rate limiting per client
- TLS/HTTPS encryption
- Pexels attribution compliance
- Content moderation checks

## Migration Path

### Current State (MVP)
- All services on same Docker Compose
- Redis ephemeral cache
- MinIO local storage

### Phase 2 (Beta)
- Add PostgreSQL for job persistence
- External Redis (ElastiCache, Memorystore)
- S3/GCS for production object storage

### Phase 3 (Production)
- Kubernetes deployment
- Service mesh (Istio optional)
- Managed database (RDS, Cloud SQL)
- CDN for video delivery
- Horizontal autoscaling

## Performance Baseline

### Typical Latencies (per 60-second video)
- Scene Planning: 0.5-1 second
- Asset Retrieval: 5-10 seconds
- TTS Generation: 5-10 seconds
- Audio Processing: 2-5 seconds
- Video Rendering: 30-120 seconds
- **Total: 45-150 seconds** (~1-2.5 minutes)

### Resource Usage (per job)
- Peak memory: 500MB - 2GB (depends on Whisper model)
- CPU: Up to 4 cores during rendering
- Network: 50-200MB (varies by clip length)

## Known Limitations

1. **MVP Scene Planning**: Simple heuristic-based, not ML-based
2. **No Actual Asset Download**: Pexels clips not actually downloaded in MVP
3. **Limited Effects**: No transitions, effects, or color grading in MVP
4. **No Persistence**: Jobs lost if services stop (Redis only)
5. **Webhook Delivery**: Not guaranteed, no retries
6. **API Authentication**: None in MVP

## Future Enhancements

### Short Term
-[ ] Persistent job storage (PostgreSQL)
- [ ] Actual Pexels asset download
- [ ] Subtitle rendering in video
- [ ] Webhook retry logic
- [ ] API key authentication

### Medium Term
- [ ] GPU-accelerated Whisper
- [ ] Advanced scene composition
- [ ] Multi-language support
- [ ] Interactive editing UI
- [ ] Cost estimation

### Long Term
- [ ] Style transfer and effects
- [ ] ML-based shot selection
- [ ] Asset versioning and rollback
- [ ] Marketplace extensions
- [ ] Enterprise SLA support
