# API Documentation

## Base URL

```
https://api.videogen.example.com
Local: http://localhost:8080
```

## Authentication

**Status**: Not implemented in MVP
- Future: API key-based authentication with authorization scopes

## Response Format

All responses are in JSON format with standard HTTP status codes.

### Success Response
```json
{
  "status": "success",
  "data": { /* endpoint-specific data */ },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": { /* optional debugging info */ }
}
```

## Endpoints

### 1. Health Check
Check if the API is running.

**Request**
```
GET /health
```

**Response** `200 OK`
```json
{
  "status": "healthy",
  "service": "api",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. Generate Video
Create a new video generation job.

**Request**
```
POST /mcp/generate
Content-Type: application/json
```

**Request Body**
```json
{
  "prompt": "A calm sunrise over a city with inspirational background music",
  "duration_target": 60,
  "style": "cinematic",
  "voice": "en-US-neutral",
  "language": "en",
  "scene_count": 4,
  "callback_url": "https://example.com/webhook/callback",
  "priority": 5
}
```

**Parameters**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| prompt | string | ✅ | - | Text prompt describing the video content |
| duration_target | integer | ❌ | 60 | Target video duration in seconds (10-600) |
| style | string | ❌ | cinematic | Video style: `cinematic`, `social`, `broadcast` |
| voice | string | ❌ | en-US-neutral | Narrator voice identifier |
| language | string | ❌ | en | Language code (e.g., en, es, fr, de, ja, zh) |
| scene_count | integer | ❌ | auto | Number of scenes (auto-calculated if omitted) |
| callback_url | string | ❌ | null | Webhook URL for completion notification |
| priority | integer | ❌ | 5 | Job priority (1-10, higher = more important) |

**Response** `202 Accepted`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "accepted",
  "message": "Job queued for processing"
}
```

**Error Examples**

Missing required prompt:
```json
{
  "error": "Missing required field: prompt",
  "code": "VALIDATION_ERROR"
}
```

Invalid duration:
```json
{
  "error": "Duration must be between 10 and 600 seconds",
  "code": "INVALID_PARAMETER"
}
```

---

### 3. Get Job Status
Check the progress of a video generation job.

**Request**
```
GET /mcp/status/{job_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "rendering",
  "overall_progress": 75.5,
  "current_step": "Rendering video with FFmpeg...",
  "logs": [
    "Job started at 2024-01-15T10:30:15Z",
    "Scene planning completed in 0.8s",
    "Retrieved 4 video clips from Pexels",
    "Generated 60s of narration audio",
    "Starting video rendering with FFmpeg"
  ],
  "scenes_processed": 3,
  "total_scenes": 4,
  "estimated_time_remaining": 45.0,
  "error": null
}
```

**Status Values**
- `pending` - Job waiting to be processed
- `scene_planning` - Breaking down prompt into scenes
- `asset_retrieval` - Fetching stock footage
- `tts_generation` - Generating narration audio
- `audio_processing` - Processing audio and generating subtitles
- `rendering` - Composing video with FFmpeg
- `completed` - Job finished successfully
- `failed` - Job failed, check error field
- `cancelled` - Job was cancelled by user

**Response** `404 Not Found`
```json
{
  "error": "Job not found",
  "code": "JOB_NOT_FOUND"
}
```

---

### 4. Get Job Result
Retrieve the completed video and related files.

**Request**
```
GET /mcp/result/{job_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response** `200 OK` (when completed)
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "video_url": "s3://videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/output.mp4",
  "thumbnail_url": "s3://videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890/thumbnail.jpg",
  "metadata": {
    "duration": 60,
    "format": "mp4",
    "resolution": "1920x1080",
    "codec": "h264",
    "bitrate": "5000k",
    "fps": 30,
    "scene_count": 4,
    "has_subtitles": true,
    "has_narration": true,
    "generated_at": "2024-01-15T10:31:45Z"
  }
}
```

**Response** `202 Accepted` (when in progress)
```json
{
  "status": "in_progress",
  "job_status": "rendering",
  "overall_progress": 75.5,
  "estimated_time_remaining": 45.0
}
```

**Response** `404 Not Found`
```json
{
  "error": "Job not found",
  "code": "JOB_NOT_FOUND"
}
```

---

### 5. Cancel Job
Stop an in-progress job.

**Request**
```
POST /mcp/cancel/{job_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "cancelled",
  "message": "Job has been cancelled"
}
```

**Error Responses**

Job already completed:
```json
{
  "error": "Cannot cancel job with status: completed",
  "code": "INVALID_STATE"
}
```

Job not found:
```json
{
  "error": "Job not found",
  "code": "JOB_NOT_FOUND"
}
```

---

### 6. Prefetch Assets
Pre-warm assets for a prompt to enable low-latency generation later.

**Request**
```
POST /mcp/prefetch
Content-Type: application/json
```

**Request Body**
```json
{
  "prompt": "A sunset over the ocean",
  "language": "en"
}
```

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | ✅ | Text prompt to prefetch |
| language | string | ❌ | Language for TTS model (default: en) |

**Response** `202 Accepted`
```json
{
  "prefetch_id": "prefetch_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "prefetch_queued",
  "message": "Assets are being pre-cached for faster generation"
}
```

---

### 7. Get Storyboard
Retrieve the intermediate storyboard with scenes and assets.

**Request**
```
GET /mcp/storyboard/{job_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "prompt": "A sunset over the ocean",
  "total_duration": 60,
  "scenes": [
    {
      "id": "scene_1",
      "description": "Golden hour on the beach with waves",
      "duration": 15,
      "keywords": ["sunset", "ocean", "beach", "waves"],
      "shot_type": "aerial",
      "clip_id": "pexels_12345",
      "clip_url": "https://videos.pexels.com/video-123",
      "start_time": 0,
      "end_time": 15
    }
  ],
  "audio_segments": [
    {
      "id": "audio_1",
      "text": "As the sun sets over the vast ocean...",
      "duration": 60,
      "language": "en",
      "speaker": "narrator"
    }
  ],
  "subtitles": [
    {
      "text": "As the sun sets over the vast ocean",
      "start_time": 0,
      "end_time": 8000
    }
  ]
}
```

**Response** `202 Accepted` (not ready yet)
```json
{
  "error": "Storyboard not yet available",
  "status": "in_progress",
  "job_status": "asset_retrieval"
}
```

---

## Webhooks

When a job completes, if `callback_url` was provided, the API will POST to that URL.

**Webhook Request**
```
POST {callback_url}
Content-Type: application/json
```

**Webhook Payload** (on success)
```json
{
  "event": "job_completed",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "video_url": "s3://videos/.../output.mp4",
  "thumbnail_url": "s3://videos/.../thumbnail.jpg",
  "generated_at": "2024-01-15T10:31:45Z"
}
```

**Webhook Payload** (on failure)
```json
{
  "event": "job_failed",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "failed",
  "error": "FFmpeg rendering failed",
  "error_code": "RENDERING_ERROR",
  "failed_at": "2024-01-15T10:31:45Z"
}
```

---

## Rate Limiting

**Status**: Not implemented in MVP

Future rate limits:
- Free tier: 10 jobs/hour, 100 minutes/day
- Pro tier: 100 jobs/hour, unlimited
- Enterprise: Custom limits

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| INVALID_PARAMETER | 400 | Invalid parameter value |
| MISSING_FIELD | 400 | Required field missing |
| JOB_NOT_FOUND | 404 | Job ID not found |
| INVALID_STATE | 400 | Cannot perform operation in current state |
| SCENE_PLANNING_ERROR | 500 | Scene planning failed |
| ASSET_RETRIEVAL_ERROR | 500 | Asset retrieval failed |
| AUDIO_GENERATION_ERROR | 500 | Audio generation failed |
| RENDERING_ERROR | 500 | Video rendering failed |
| PEXELS_API_ERROR | 503 | Pexels API error |
| STORAGE_ERROR | 500 | Storage access error |
| INTERNAL_ERROR | 500 | Internal server error |

---

## Examples

### cURL

```bash
# Generate video
curl -X POST http://localhost:8080/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A peaceful forest with birds flying",
    "duration_target": 90,
    "style": "cinematic"
  }'

# Check status
curl http://localhost:8080/mcp/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Get result
curl http://localhost:8080/mcp/result/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Cancel job
curl -X POST http://localhost:8080/mcp/cancel/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Python

```python
import requests

# Generate
response = requests.post(
    "http://localhost:8080/mcp/generate",
    json={
        "prompt": "A forest with birds",
        "duration_target": 90
    }
)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8080/mcp/status/{job_id}").json()
print(f"Status: {status['status']}, Progress: {status['overall_progress']}%")

# Get result
result = requests.get(f"http://localhost:8080/mcp/result/{job_id}").json()
print(f"Video: {result['video_url']}")
```

### JavaScript

```javascript
// Generate
const response = await fetch("http://localhost:8080/mcp/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    prompt: "A forest with birds",
    duration_target: 90
  })
});
const { job_id } = await response.json();

// Check status
const status = await fetch(
  `http://localhost:8080/mcp/status/${job_id}`
).then(r => r.json());
console.log(`Status: ${status.status}, Progress: ${status.overall_progress}%`);

// Get result
const result = await fetch(
  `http://localhost:8080/mcp/result/${job_id}`
).then(r => r.json());
console.log(`Video: ${result.video_url}`);
```

---

## Changelog

### v1.0.0 (Initial MVP)
- POST /mcp/generate
- GET /mcp/status/{job_id}
- GET /mcp/result/{job_id}
- POST /mcp/cancel/{job_id}
- POST /mcp/prefetch
- GET /mcp/storyboard/{job_id}

### Future Versions
- [ ] Batch generation support
- [ ] Advanced editing endpoints
- [ ] Style transfer endpoints
- [ ] Asset management endpoints
- [ ] Analytics endpoints
