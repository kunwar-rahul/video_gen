### Project Overview

Build a **scalable text-to-video service** that accepts text prompts and produces videos of arbitrary length by combining stock clips from **Pexels**, audio generation and transcription via **Whisper**, and an orchestration layer that exposes an **MCP server**-compatible API so any AI model or external service can call it. The system runs as a **Docker container** (GPU-capable optional) and includes tooling for caching, quota control, editing, and advanced creative features (style transfer, scene planning, multi-language narration, timeline editing, and webhooks).

---

### Key components and responsibilities

| **Component** | **Primary responsibility** | **Why it matters** |
|---|---:|---|
| **API Gateway / MCP Server** | Expose REST/gRPC endpoints and MCP-compatible RPCs for model integration | Enables plug-and-play integration with AI models and external orchestrators |
| **Orchestrator / Job Manager** | Accepts text jobs, schedules tasks, manages retries, progress, and webhooks | Handles long-running video generation reliably |
| **Asset Retriever (Pexels)** | Search and fetch video clips and images from Pexels based on semantic queries | Provides high-quality stock footage for scenes.  |
| **Speech / ASR (Whisper)** | Transcribe audio, detect language, and optionally generate narration text-to-speech pipeline | Enables subtitle generation, language detection, and voice-over alignment.  |
| **Renderer / Composer** | Stitch clips, overlays, transitions, captions, audio, and effects into final video | Core video assembly engine (FFmpeg + custom compositor) |
| **Storage** | Object store for intermediate assets and final videos (S3-compatible) | Durable, scalable storage for large media files |
| **Cache / CDN** | Cache frequently used clips and serve final assets | Reduces Pexels API calls and speeds delivery |
| **Auth / Billing / Quotas** | API keys, rate limits, usage tracking, billing hooks | Protects resources and monetizes the service |
| **Monitoring / Logging** | Metrics, traces, job logs, alerting | Operational visibility and reliability |

---

### High-level architecture and data flow

1. **Client or AI model** calls the MCP server endpoint with a text prompt and optional parameters (style, length, voice, language).
2. **Orchestrator** breaks the prompt into scenes using an internal scene planner (NLP) and maps each scene to search queries.
3. **Asset Retriever** queries Pexels for matching clips, downloads them, and stores them in object storage. 
4. **Audio pipeline**: generate TTS narration (or accept user audio), run Whisper for ASR or language detection, produce subtitles and timing. 
5. **Renderer** composes clips, transitions, captions, and audio into a timeline and exports the final video via FFmpeg.
6. **Delivery**: final video stored in object storage and optionally pushed to CDN; webhook or MCP callback notifies the caller.

---

### API design and MCP server capability

#### Core endpoints
- **POST /mcp/generate** — Accepts `prompt`, `duration_target`, `style`, `voice`, `language`, `scene_count`, `callback_url`, `priority`.
- **GET /mcp/status/{job_id}** — Job progress, current step, logs, estimated time.
- **GET /mcp/result/{job_id}** — Signed URL to final video and thumbnails.
- **POST /mcp/cancel/{job_id}** — Cancel job.
- **POST /mcp/prefetch** — Pre-warm assets for a prompt (useful for low-latency demos).

#### MCP integration details
- **MCP-compatible RPC**: expose a gRPC endpoint that mirrors the REST endpoints and supports streaming progress updates and chunked logs so AI models can poll or subscribe to job state.
- **Model hooks**: allow models to request intermediate artifacts (storyboard JSON, per-scene clips) for further model-driven editing.
- **Authentication**: token-based auth with scopes (read/write/admin) and per-token quotas.

---

### Processing pipeline details

#### Scene planning and retrieval
- **Scene planner**: NLP module that splits text into scenes, assigns durations, and generates search keywords and shot types (close-up, aerial, slow-motion).
- **Semantic search**: use prompt embeddings to expand queries (synonyms, mood words) before calling Pexels.
- **Pexels usage**: respect API rate limits and caching; prefetch multiple candidate clips per scene and rank by visual match and duration. 

#### Audio and subtitles
- **TTS options**: integrate multiple TTS engines (open-source and cloud) with SSML support for prosody.
- **Whisper**: use Whisper for language detection and transcription of user audio or generated narration to produce accurate subtitles and timing. Whisper can be containerized and GPU-accelerated for speed. 
- **Alignment**: align subtitles to timeline using word-level timestamps from Whisper or forced-alignment tools.

#### Rendering and effects
- **Compositor**: FFmpeg + custom filters for transitions, color grading, overlays, and motion text.
- **Advanced effects**: optional neural style transfer, motion stabilization, and AI-driven color grading per scene.
- **Quality profiles**: presets for social, cinematic, and broadcast outputs.

---

### Dockerization and deployment

#### Docker strategy
- **Microservices**: each major component runs in its own container (API/MCP server, orchestrator, retriever, whisper worker, renderer).
- **GPU support**: provide a CUDA-enabled Dockerfile for Whisper and renderer workers; fallback CPU images for low-cost deployments.
- **Single-container dev image**: a lightweight dev image that runs all services for local testing.

#### Example Dockerfile for Whisper worker (GPU)
```dockerfile
FROM nvidia/cuda:12.2-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg git
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY whisper_worker /app/whisper_worker
CMD ["python3", "whisper_worker/main.py"]
```

#### Example docker-compose for local dev
```yaml
version: "3.8"
services:
  api:
    build: ./api
    ports: ["8080:8080"]
    environment:
      - STORAGE_URL=http://minio:9000
  orchestrator:
    build: ./orchestrator
  retriever:
    build: ./retriever
    environment:
      - PEXELS_API_KEY=${PEXELS_API_KEY}
  whisper:
    build: ./whisper
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  renderer:
    build: ./renderer
  minio:
    image: minio/minio
    command: server /data
    ports: ["9000:9000"]
```

**Run**: `docker-compose up --build` for local dev. For production, use Kubernetes with GPU node pools and a managed object store.

---

### Advanced features and imaginative extensions

- **Adaptive length scaling**: automatically expand or compress scenes to meet any target duration while preserving narrative flow.
- **Multi-language narration**: auto-translate prompt and generate TTS in target language; use Whisper for quality checks.
- **Style transfer and lookbooks**: apply a “lookbook” (color grade + LUT + motion style) to entire video for consistent aesthetics.
- **Interactive storyboard editor**: web UI to preview and swap candidate clips per scene before final render.
- **AI-driven shot selection**: use a vision model to score Pexels clips for emotional match and composition.
- **Versioning and undo**: keep timeline versions and allow model-driven iterative edits.
- **Real-time preview**: low-res streaming preview while full render continues.
- **Plugin system**: allow third-party tools (audio mastering, face retouching) to register as pipeline steps.
- **Enterprise features**: watermarking, legal metadata tracking for Pexels assets, and automated credit generation.

---

### Security, compliance, and cost controls

- **API keys and scopes**: per-client keys with quotas and rate limits.
- **Pexels compliance**: track and store attribution metadata for each clip to comply with licensing. 
- **Content moderation**: automated checks for disallowed content before rendering.
- **Cost controls**: job cost estimation, pre-approval for expensive renders, and per-tenant budgets.
- **Data retention**: configurable retention policies for intermediate assets and final videos.

---

### Monitoring, observability, and SLOs

- **Metrics**: job queue length, average render time, Pexels API calls, Whisper latency, GPU utilization.
- **Tracing**: distributed traces across orchestrator, retriever, whisper, and renderer.
- **SLO examples**: 95% of short jobs (<2 minutes) complete within 2 minutes on GPU nodes; 99% of API calls authenticated.

---

### Roadmap and milestones

1. **MVP (2–4 weeks)**  
   - REST + MCP endpoints, basic scene planner, Pexels integration, FFmpeg renderer, Whisper CPU worker, Docker compose dev setup. 
2. **Beta (4–8 weeks)**  
   - GPU Whisper worker, TTS integration, subtitles, job persistence, webhooks, basic UI.
3. **Production (8–16 weeks)**  
   - Kubernetes deployment, CDN, caching, billing, advanced effects, enterprise features.
4. **Advanced features (ongoing)**  
   - Style transfer, interactive editor, plugin marketplace, multi-language scaling.

---

### Example job JSON and flow

**Request**
```json
{
  "prompt": "A calm sunrise over a city, inspirational music, 90 seconds, cinematic",
  "duration_target": 90,
  "style": "cinematic",
  "voice": "en-US-female",
  "callback_url": "https://example.com/webhook"
}
```

**Flow**
- MCP server accepts job and returns `job_id`.
- Orchestrator creates storyboard, calls Pexels for 6 candidate clips, downloads top picks.
- TTS generates narration; Whisper verifies and timestamps.
- Renderer composes timeline and exports MP4.
- Callback sent with signed URL.

---

### File structure suggestion

```
/app
  /api
  /orchestrator
  /retriever
  /whisper_worker
  /renderer
  /ui
  /infra
    docker-compose.yml
    k8s/
  /docs
```

---

### Final recommendations

- **Start with a modular MVP**: REST + MCP server, Pexels retrieval, FFmpeg renderer, Whisper CPU worker in Docker Compose.   
- **Add GPU support early** for Whisper and renderer to reduce latency for longer videos.   
- **Instrument everything** from day one (metrics, traces, cost estimation) so you can scale safely.  
- **Respect Pexels attribution and rate limits** and implement caching to reduce API usage. 
