# Enhancement Plan: Jobs Endpoint & Web Interface

## Overview
Enhance the video generation service with a unified jobs management endpoint and build a complete web interface for job submission, monitoring, and analytics.

---

## 1. New API Endpoint: GET /mcp/jobs

### Specification
**Endpoint**: `GET /mcp/jobs`

**Purpose**: List all jobs with comprehensive filtering, sorting, and pagination

**Query Parameters**:
- `status` (string, optional): Filter by status (pending, scene_planning, asset_retrieval, tts_generation, audio_processing, rendering, completed, failed, cancelled)
- `date_range` (string, optional): Filter by date range (today, week, month, all)
- `priority` (integer, optional): Filter by priority level (1-10)
- `limit` (integer, optional, default: 50): Maximum records per page
- `offset` (integer, optional, default: 0): Pagination offset
- `sort_by` (string, optional): Sort column (created_at, updated_at, progress, duration_target, priority)
- `sort_order` (string, optional): asc or desc (default: desc)

**Response** `200 OK`:
```json
{
  "jobs": [
    {
      "job_id": "uuid",
      "prompt": "A sunset over the ocean...",
      "status": "rendering",
      "overall_progress": 75.5,
      "duration_target": 60,
      "style": "cinematic",
      "priority": 5,
      "created_at": "2024-01-15T10:30:15Z",
      "updated_at": "2024-01-15T10:35:30Z",
      "estimated_time_remaining": 45.0
    }
  ],
  "pagination": {
    "total": 245,
    "limit": 50,
    "offset": 0,
    "page": 1,
    "pages": 5
  },
  "summary": {
    "total_jobs": 245,
    "completed": 180,
    "failed": 15,
    "in_progress": 35,
    "pending": 15
  }
}
```

**Error Handling**:
- Invalid filter: 400 Bad Request
- Unauthorized: 401 Unauthorized (future)
- Internal error: 500 Internal Server Error

---

## 2. Web Application Architecture

### Technology Stack

**Frontend**:
- React 18+ with TypeScript
- Redux Toolkit for state management
- Material-UI v5 or Tailwind CSS for styling
- Recharts or Chart.js for analytics visualization
- Socket.io-client for WebSocket real-time updates
- Axios for HTTP requests
- React Router for navigation
- Formik + Yup for form validation

**Real-time Communication**:
- WebSocket (Socket.io) for live progress updates
- Server-Sent Events (SSE) as fallback
- Polling as secondary fallback (5-second intervals)

**Backend Enhancements**:
- WebSocket server (Port 8085)
- Redis pub/sub for broadcasting job updates
- Session management (Redis-based)

**Deployment**:
- Development: Vite or Create React App
- Production: Static build, Nginx reverse proxy
- Docker: Multi-stage build (Node.js → npm build → Nginx serve)

---

## 3. Web Interface Components

### Layout Structure
```
┌─────────────────────────────────────────────────────┐
│  Header (Logo, Nav, User Menu, Notifications)       │
├─────────────────────────────────────────────────┬───┤
│  Sidebar                │  Main Content          │   │
│  • Dashboard            │  ┌──────────────────┐ │   │
│  • Job List             │  │  Selected Page   │ │   │
│  • Create Video         │  │  (Dynamic)       │ │   │
│  • Analytics            │  │                  │ │   │
│  • Settings             │  └──────────────────┘ │   │
├─────────────────────────────────────────────────┴───┤
│  Footer (Status, Links, Copyright)                  │
└─────────────────────────────────────────────────────┘
```

### Core Pages

#### 1. Dashboard (Default Landing)
**Purpose**: At-a-glance overview of service health and recent activity

**Components**:
- **KPI Cards**: Total jobs, success rate, avg render time, queue depth
- **Status Chart**: Pie chart of job statuses (completed, failed, in-progress, pending)
- **Activity Timeline**: Recent job completions/failures
- **Queue Depth**: Real-time bar chart of jobs in each processing stage
- **Quick Stats**: Pexels API usage, cache hit rate, average job duration

**Interactions**:
- Click on any category to filter Job List
- Edit webhook URL and API settings
- Download daily/weekly/monthly reports

#### 2. Job List & Management
**Purpose**: View, filter, and manage all jobs

**Features**:
- **Filterable Table**:
  - Columns: Job ID, Prompt (truncated), Status, Progress, Duration, Created, Actions
  - Sort by any column
  - Filter dropdown: Status, Priority, Date Range
  - Search by job ID or prompt keywords
  - Show X records per page (10, 25, 50, 100)

- **Status Badge Colors**:
  - Pending: Gray
  - Scene Planning: Blue
  - Asset Retrieval: Cyan
  - TTS Generation: Purple
  - Audio Processing: Magenta
  - Rendering: Orange
  - Completed: Green
  - Failed: Red
  - Cancelled: Dark Gray

- **Row Actions**:
  - View Details (click row)
  - Copy Job ID
  - Cancel Job (if in-progress)
  - Download Result (if completed)
  - Retry Job (if failed)

- **Bulk Actions** (select multiple):
  - Cancel Selected
  - Export Selected
  - Download Results

- **Pagination**: Previous/Next, Jump to page, Show total count

#### 3. Job Detail Page
**Purpose**: Deep dive into a single job with monitoring and controls

**Sections**:
1. **Header**:
   - Job ID (copyable)
   - Status badge (live-updating)
   - Action buttons: Cancel, Retry, Download, Share
   - Timestamps: Created, Started, Completed

2. **Request Summary**:
   - Prompt (full text, expandable)
   - Parameters: duration_target, style, voice, language
   - Priority level
   - Callback URL (if set)

3. **Progress Section** (Live-Updated):
   - Overall progress bar (0-100%)
   - Stage breakdown:
     - Scene Planning: ▓▒░ 20%
     - Asset Retrieval: ▓▓▓ 40%
     - Audio Processing: ▓▓▓ 60%
     - Rendering: ▓▓░░ (current)
   - Estimated time remaining
   - Current step description

4. **Logs Viewer**:
   - Auto-scrolling terminal-style output
   - Search/filter logs
   - Log levels: INFO, DEBUG, ERROR, WARNING
   - Timestamp on each log entry
   - Export logs as text file

5. **Storyboard Preview** (when available):
   - Grid of scene thumbnails with durations
   - Scene descriptions and keywords
   - Clip information (Pexels ID, duration, user attribution)

6. **Video Player** (when completed):
   - HLS.js streaming player
   - Playback controls: play, pause, volume, fullscreen
   - Quality selector: 480p, 720p, 1080p (if available)
   - Timeline scrubber with thumbnails on hover
   - Subtitle toggle (on/off, select language)
   - Download button (MP4, WebM, etc.)
   - Share menu: Copy link, social media, email

#### 4. Quick Generate Form
**Purpose**: Simple, fast video creation for non-technical users

**Form Fields**:
1. **Prompt** (required)
   - Text area with character counter
   - Placeholder suggestions
   - AI prompt enhancement button (optional)

2. **Quick Presets** (radio buttons):
   - ⭐ Cinematic (1920x1080, slow, music + narration)
   - 📱 Social Media (1080x1080, fast, captions)
   - 🎓 Educational (1280x720, medium, narration only)
   - 🎬 Custom (show all options below)

3. **Duration**:
   - Slider: 10s - 600s
   - Auto-calculate scene count
   - Display estimated processing time

4. **Optional Parameters** (collapsible):
   - Style dropdown: cinematic, social, broadcast, custom
   - Voice dropdown: en-US-neutral, en-US-female, en-US-male, multi-language
   - Language selector: English, Spanish, French, German, Japanese, Chinese
   - Callback URL (for webhooks)
   - Priority: Low, Normal, High

5. **Submit**:
   - Generate button
   - Loading state with estimated queue position
   - Success: Show job ID, option to track or create another

#### 5. Analytics Dashboard
**Purpose**: Insights into service performance and usage patterns

**Metrics Visualizations**:
1. **Job Success Rate** (Line chart):
   - 7-day view with daily breakdown
   - 30-day monthly aggregate
   - Toggle: Success %, Completed jobs, Failed jobs

2. **Render Time Analysis** (Bar chart):
   - By video length (0-60s, 60-120s, 120-300s, 300s+)
   - By style (cinematic, social, broadcast)
   - Breakdown: avg, min, max, p95

3. **Queue Depth** (Real-time area chart):
   - Jobs in each stage (stacked)
   - Auto-update every 10 seconds
   - Peak queue size indicator

4. **Pexels API Usage** (Gauge + line chart):
   - Current calls/hour vs rate limit
   - Cache hit ratio (%)
   - Historical trend (24h)

5. **Cost Estimation** (if enabled):
   - Estimated cost per job (by length, quality)
   - Total cost this month
   - Projected monthly cost
   - Cost breakdown: compute, storage, Pexels API

6. **User Activity**:
   - Jobs submitted (today, this week, this month)
   - Top styles used
   - Top voices used
   - Most common durations

7. **Health Status**:
   - Service uptime %
   - API response time (p50, p95, p99)
   - Webhook delivery success rate

#### 6. Settings/Configuration
**Purpose**: Manage API keys, preferences, and integrations

**Sections**:
1. **API Keys**:
   - Display current key (masked)
   - Copy to clipboard
   - Regenerate key (with confirmation)
   - Revoke key
   - Show key creation date and last used

2. **Webhook Configuration**:
   - Callback URL for job completion
   - Retry policy (exponential backoff, max retries)
   - Delivery logs (show recent webhooks sent)
   - Test webhook button

3. **User Preferences**:
   - Default style, voice, language
   - Preferred quality (720p, 1080p, 2K)
   - Auto-play videos on completion
   - Dark/light theme toggle

4. **Rate Limits & Quotas** (if implemented):
   - Current usage: X/Y jobs per hour
   - Max concurrent jobs
   - Total storage quota

5. **Download History**:
   - Export all job metadata (JSON, CSV)
   - Export cost report
   - Clear local cache

---

## 4. WebSocket Real-time Updates

### Events

**Client → Server**:
- `subscribe_job` - Start listening to job updates
  ```json
  { "event": "subscribe_job", "job_id": "uuid" }
  ```

- `subscribe_all_jobs` - Listen to all job events
  ```json
  { "event": "subscribe_all_jobs", "filters": { "status": "rendering" } }
  ```

- `unsubscribe_job` - Stop listening to specific job
  ```json
  { "event": "unsubscribe_job", "job_id": "uuid" }
  ```

**Server → Client**:
- `job_status_update` - Job status changed
  ```json
  {
    "event": "job_status_update",
    "job_id": "uuid",
    "status": "rendering",
    "overall_progress": 75.5,
    "current_step": "Rendering video...",
    "estimated_time_remaining": 45
  }
  ```

- `job_log_entry` - New log line
  ```json
  {
    "event": "job_log_entry",
    "job_id": "uuid",
    "timestamp": "2024-01-15T10:35:30Z",
    "level": "INFO",
    "message": "Rendering frame 1500/1800"
  }
  ```

- `job_completed` - Job finished
  ```json
  {
    "event": "job_completed",
    "job_id": "uuid",
    "video_url": "s3://videos/uuid/output.mp4",
    "thumbnail_url": "s3://videos/uuid/thumbnail.jpg"
  }
  ```

- `job_failed` - Job failed
  ```json
  {
    "event": "job_failed",
    "job_id": "uuid",
    "error": "FFmpeg rendering failed",
    "error_code": "RENDERING_ERROR"
  }
  ```

- `queue_updated` - Queue statistics changed
  ```json
  {
    "event": "queue_updated",
    "pending": 5,
    "processing": 3,
    "completed": 1200
  }
  ```

---

## 5. File Structure

```
video_gen/
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── websocket_server.py (NEW)
│   ├── common/
│   ├── orchestrator/
│   ├── retriever/
│   ├── whisper_worker/
│   └── renderer/
│
├── ui/ (NEW)
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── logo.svg
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Layout.tsx
│   │   │   │
│   │   │   ├── jobs/
│   │   │   │   ├── JobList.tsx
│   │   │   │   ├── JobDetail.tsx
│   │   │   │   ├── JobForm.tsx
│   │   │   │   ├── QuickGenerate.tsx
│   │   │   │   └── VideoPlayer.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── KPICards.tsx
│   │   │   │   ├── StatusChart.tsx
│   │   │   │   └── ActivityTimeline.tsx
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   ├── AnalyticsDashboard.tsx
│   │   │   │   ├── SuccessRateChart.tsx
│   │   │   │   ├── RenderTimeAnalysis.tsx
│   │   │   │   └── QueueDepthChart.tsx
│   │   │   │
│   │   │   └── settings/
│   │   │       ├── Settings.tsx
│   │   │       ├── APIKeyManagement.tsx
│   │   │       └── WebhookConfig.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── JobListPage.tsx
│   │   │   ├── JobDetailPage.tsx
│   │   │   ├── GeneratePage.tsx
│   │   │   ├── AnalyticsPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts (REST API client)
│   │   │   ├── websocket.ts (WebSocket client)
│   │   │   └── storage.ts (localStorage helpers)
│   │   │
│   │   ├── store/
│   │   │   ├── jobSlice.ts
│   │   │   ├── analyticsSlice.ts
│   │   │   ├── uiSlice.ts
│   │   │   └── store.ts
│   │   │
│   │   ├── types/
│   │   │   └── index.ts (TypeScript interfaces)
│   │   │
│   │   ├── hooks/
│   │   │   ├── useJobs.ts
│   │   │   └── useWebSocket.ts
│   │   │
│   │   ├── styles/
│   │   │   ├── global.css
│   │   │   └── theme.ts
│   │   │
│   │   ├── App.tsx
│   │   └── index.tsx
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml (updated with UI service)
├── docs/
│   ├── WEB_INTERFACE.md (NEW)
│   ├── JOBS_API.md (NEW)
│   └── ...
```

---

## 6. Implementation Plan

### Phase 1: Core API (Week 1-2)
- [ ] Implement GET /mcp/jobs endpoint with filtering
- [ ] Add pagination support
- [ ] Create database queries for job listing
- [ ] Write tests for jobs endpoint
- [ ] Document API in API.md

### Phase 2: WebSocket Infrastructure (Week 2-3)
- [ ] Set up WebSocket server (Socket.io)
- [ ] Implement Redis pub/sub for job updates
- [ ] Create job event broadcasting system
- [ ] Test real-time updates with multiple clients

### Phase 3: Frontend Scaffolding (Week 3-4)
- [ ] Initialize React project with Vite/CRA
- [ ] Set up TypeScript, Redux, Material-UI
- [ ] Create layout and routing
- [ ] Implement API and WebSocket services

### Phase 4: Core Pages (Week 4-5)
- [ ] Build Dashboard
- [ ] Build Job List page
- [ ] Build Job Detail page
- [ ] Build Quick Generate form
- [ ] Connect to API endpoints

### Phase 5: Advanced Features (Week 5-6)
- [ ] Analytics Dashboard
- [ ] Settings page
- [ ] Video player integration
- [ ] Real-time WebSocket updates

### Phase 6: Polish & Deployment (Week 6-7)
- [ ] Complete responsive design
- [ ] Performance optimization
- [ ] Docker containerization
- [ ] Documentation
- [ ] Testing and bug fixes

---

## 7. API Endpoint Implementation Example

```python
@app.route("/mcp/jobs", methods=["GET"])
def list_jobs():
    """List all jobs with filtering and pagination."""
    try:
        # Get query parameters
        status = request.args.get("status")
        date_range = request.args.get("date_range", "all")
        priority = request.args.get("priority", type=int)
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        sort_by = request.args.get("sort_by", "created_at")
        sort_order = request.args.get("sort_order", "desc")
        
        # Validate parameters
        if limit > 100:
            limit = 100  # Cap at 100
        
        # Build query
        query_filters = {}
        if status:
            query_filters["status"] = status
        if priority:
            query_filters["priority"] = priority
        
        # Apply date range filter
        if date_range != "all":
            query_filters["date_range"] = date_range
        
        # Get total count
        total = len([j for j in job_cache._cache.items() if match_filters(j, query_filters)])
        
        # Get paginated results
        jobs = []
        for job_id, job_data in list(job_cache._cache.items())[offset:offset+limit]:
            if match_filters(job_data, query_filters):
                jobs.append({
                    "job_id": job_id,
                    "prompt": job_data.get("prompt", "")[:100],
                    "status": job_data.get("status", "pending"),
                    "overall_progress": job_data.get("overall_progress", 0),
                    "created_at": job_data.get("created_at"),
                    "updated_at": job_data.get("updated_at"),
                })
        
        return jsonify({
            "jobs": jobs,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "page": (offset // limit) + 1,
                "pages": (total + limit - 1) // limit
            },
            "summary": get_jobs_summary()
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

---

## 8. TypeScript Types Example

```typescript
// types/index.ts

export interface Job {
  job_id: string;
  prompt: string;
  status: JobStatus;
  overall_progress: number;
  duration_target: number;
  style: string;
  voice: string;
  language: string;
  priority: number;
  created_at: string;
  updated_at: string;
  estimated_time_remaining: number;
  error?: string;
}

export type JobStatus = 
  | "pending"
  | "scene_planning"
  | "asset_retrieval"
  | "tts_generation"
  | "audio_processing"
  | "rendering"
  | "completed"
  | "failed"
  | "cancelled";

export interface JobsListResponse {
  jobs: Job[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    page: number;
    pages: number;
  };
  summary: {
    total_jobs: number;
    completed: number;
    failed: number;
    in_progress: number;
    pending: number;
  };
}

export interface GenerateRequest {
  prompt: string;
  duration_target?: number;
  style?: string;
  voice?: string;
  language?: string;
  scene_count?: number;
  callback_url?: string;
  priority?: number;
}
```

---

## 9. Deployment Configuration

### Docker Compose Update
```yaml
services:
  # ... existing services ...
  
  frontend:
    build:
      context: ./ui
      dockerfile: Dockerfile
    container_name: video-gen-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://api:8080
      - REACT_APP_WS_URL=ws://websocket:8085
    depends_on:
      - api
    networks:
      - video-gen-network
    restart: unless-stopped

  websocket:
    build:
      context: ./app/api
      dockerfile: Dockerfile.websocket
    container_name: video-gen-websocket
    ports:
      - "8085:8085"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - video-gen-network
    restart: unless-stopped
```

---

## 10. Deployment Steps

### Development
```bash
# Local setup
cd ui
npm install
npm run dev

# Runs on http://localhost:5173 (Vite) or 3000 (CRA)
# API proxied to http://localhost:8080
```

### Production
```bash
# Build static assets
cd ui
npm run build

# Output: ui/dist/

# Serve with Nginx or static host
# Update docker-compose.yml to serve from dist/
```

---

## 11. Success Metrics

- ✅ Jobs endpoint supports 100k+ records with <500ms response
- ✅ WebSocket delivers updates within 500ms
- ✅ Web UI loads in <3s on 4G connection
- ✅ 95%+ uptime for web UI
- ✅ Support 1000+ concurrent WebSocket connections
- ✅ Responsive design works on mobile (320px+)

---

## 12. Future Enhancements

- Interactive storyboard editor (drag-drop scene reordering)
- Batch job submission (CSV upload)
- Advanced filtering (regex, date ranges, custom)
- Export/import job templates
- User accounts and role-based access
- Two-factor authentication
- Audit logging
- Real-time collaboration (multiple users monitoring same job)
- Mobile app (React Native)
