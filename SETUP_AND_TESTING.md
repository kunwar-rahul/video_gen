# Complete Setup & Testing Guide

## Quick Start (3 Commands)

```bash
# Terminal 1: Backend (API + WebSocket)
python run_all_services.py

# Terminal 2: Frontend
cd ui && npm install && npm run dev

# Terminal 3: API Testing
python test_api_comprehensive.py
```

## Architecture

```
Video Generation Service (2026)
├── Backend (Python)
│   ├── API Server (Port 8080)
│   │   ├── REST endpoints
│   │   ├── Job management
│   │   └── Status tracking
│   ├── WebSocket Server (Port 8085)
│   │   ├── Real-time updates
│   │   ├── Job status broadcasts
│   │   └── Log streaming
│   └── Microservices
│       ├── Orchestrator
│       ├── Retriever (Pexels)
│       ├── Whisper Worker
│       └── Renderer (FFmpeg)
│
└── Frontend (React/TypeScript)
    ├── Port 3000 (Dev)
    ├── Material-UI Components
    ├── Redux State Management
    └── Socket.io Real-time Updates
```

## Completed Components

### ✅ Phase 1: Core API
- [x] GET /mcp/generate - Submit video generation job
- [x] GET /mcp/status - Get job status  
- [x] GET /mcp/jobs - List jobs with filtering, sorting, pagination
- [x] GET /mcp/result - Get video result
- [x] POST /mcp/cancel - Cancel job
- [x] GET /mcp/storyboard - Get scene storyboard
- [x] POST /mcp/prefetch - Prefetch assets

### ✅ Phase 2: WebSocket Infrastructure
- [x] WebSocket Server (Port 8085)
- [x] Event Broadcasting System
  - [x] job_status_update
  - [x] job_log_entry
  - [x] job_completed
  - [x] job_failed
  - [x] queue_updated
- [x] Event Manager (Bridge pattern)
- [x] Client subscription system

### ✅ Phase 3: React Frontend Scaffolding
- [x] Vite build setup
- [x] TypeScript configuration
- [x] Redux Toolkit store
- [x] Material-UI theme system
- [x] Type definitions for all API endpoints
- [x] Custom hooks (useJobs, useJobDetails, useWebSocket)
- [x] API client with Axios
- [x] WebSocket client with Socket.io

### ✅ Phase 4: Core Pages (All Built)
- [x] **Dashboard**: KPIs, status charts, recent activity
- [x] **Jobs List**: Filterable table, pagination, bulk actions
- [x] **Job Detail**: Progress tracking, logs, video player, cancel action
- [x] **Quick Generate**: Simple form for video creation
- [x] **Layout**: Responsive sidebar, AppBar with theme toggle
- [x] **Error Boundaries**: Error handling & user feedback

### ✅ Phase 5: Advanced Features
- [x] **Analytics**: Time series, success rates, performance metrics
- [x] **Settings**: Theme, notifications, preferences
- [x] **Responsive Design**: Mobile-friendly Material-UI components
- [x] **Real-time Updates**: WebSocket integration with fallback to polling

### ✅ Phase 6: Package & Documentation
- [x] Environment configuration (.env.example, .env.local)
- [x] README documentation
- [x] ESLint + TypeScript strict mode
- [x] Path aliases for clean imports
- [x] Production build configuration
- [x] Comprehensive type safety

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+ (for frontend)
- Redis (for job queue)
- FFmpeg (for video rendering)

### Backend Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings (Pexels API key, etc.)

# 3. Start all services (API + WebSocket)
python run_all_services.py
```

**Services will be available at:**
- API Server: http://localhost:8080
- WebSocket: ws://localhost:8085
- Health Check: http://localhost:8080/health

### Frontend Setup

```bash
# 1. Enter frontend directory
cd ui

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env.local

# 4. Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Testing

```bash
# Run comprehensive API tests
python test_api_comprehensive.py

# Run frontend type checking
cd ui && npm run type-check

# Run frontend linting
cd ui && npm run lint

# Build frontend for production
cd ui && npm run build
```

## API Endpoints

### Job Management
```
POST   /mcp/generate           - Create video generation job
GET    /mcp/status/:jobId      - Get job status
GET    /mcp/jobs              - List all jobs (with filtering)
POST   /mcp/cancel/:jobId     - Cancel a job
GET    /mcp/result/:jobId     - Get video result
GET    /mcp/storyboard/:jobId - Get scene storyboard
POST   /mcp/prefetch/:jobId   - Prefetch assets
```

### Query Parameters (GET /mcp/jobs)
```
status      - Filter by job status (queued, planning, rendering, completed, failed)
priority    - Filter by priority (low, medium, high, critical)  
date_range  - Filter by date (today, week, month, all)
limit       - Results per page (max 100, default 50)
offset      - Pagination offset (default 0)
sort_by     - Sort column (created_at, updated_at, progress, duration, priority)
sort_order  - Sort direction (asc, desc)
```

## WebSocket Events

### Client -> Server
```
subscribe_job(jobId)    - Subscribe to job updates
unsubscribe_job(jobId)  - Unsubscribe from job updates
get_active_jobs()       - Get active job count
```

### Server -> Client
```
job_status_update       - {jobId, status, progress, timestamp}
job_log_entry          - {jobId, level, message, timestamp}
job_completed          - {jobId, videoUrl, duration, timestamp}
job_failed             - {jobId, errorMessage, timestamp}
queue_updated          - {queued, processing, timestamp}
```

## Project Structure

```
video_gen/
├── app/
│   ├── api/                    # REST API server
│   │   ├── main.py            # Flask API routes
│   │   └── jobs_service.py    # Job filtering utilities
│   ├── websocket/             # WebSocket server
│   │   ├── main.py            # Socket.io setup
│   │   └── events.py          # Event broadcasting
│   ├── common/                 # Shared utilities
│   │   ├── models.py          # Data models
│   │   ├── config.py          # Configuration
│   │   └── utils.py           # Logging, caching
│   ├── orchestrator/           # Job orchestration
│   ├── retriever/              # Asset retrieval
│   ├── whisper_worker/         # Audio processing
│   └── renderer/               # Video rendering
├── ui/                         # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API/WebSocket clients
│   │   ├── store/             # Redux configuration
│   │   ├── types/             # TypeScript definitions
│   │   └── hooks/             # Custom hooks
│   ├── package.json           # Dependencies
│   ├── vite.config.ts         # Build configuration
│   └── tsconfig.json          # TypeScript config
├── local_dev.py               # Local development launcher
├── run_all_services.py        # Backend service launcher
├── websocket_server.py        # Standalone WebSocket server
├── test_api_comprehensive.py  # API test suite
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Container orchestration
└── README.md                  # Project documentation
```

## Troubleshooting

### API Not Responding
```bash
# Check if API server is running
curl http://localhost:8080/health

# Restart services
python run_all_services.py
```

### WebSocket Connection Failed
- App gracefully falls back to polling
- Check WebSocket server: ws://localhost:8085
- Check browser console for connection errors

### Frontend Build Issues
```bash
cd ui
rm -rf node_modules package-lock.json
npm install
npm run type-check
```

### Redis Connection Error
```bash
# Ensure Redis is running
redis-cli ping
# Should return: PONG

# Or run with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

## Performance Optimization

### Frontend
- Tree-shaking enabled in Vite
- Code splitting per route
- Redux state normalization
- Debounced API calls
- Image lazy loading

### Backend
- Redis caching for job data
- Job queue with Celery
- Async microservices
- Connection pooling for object storage

## Deployment

### Docker Deployment
```bash
# Build all services
docker-compose build

# Run all containers
docker-compose up -d
```

### Production Frontend Build
```bash
cd ui
npm run build
# Output in: ui/dist/
```

Deploy `ui/dist/` to static hosting (Netlify, Vercel, S3, etc.)

## Development Workflow

1. **Local Testing**
   - Start services: `python run_all_services.py`
   - Start frontend: `cd ui && npm run dev`
   - Run tests: `python test_api_comprehensive.py`

2. **API Development**
   - Edit `app/api/main.py`
   - Add new routes/endpoints
   - Test with `test_api_comprehensive.py`

3. **Frontend Development**
   - Edit components in `ui/src/`
   - Hot reload automatic (Vite)
   - Type-check: `npm run type-check`

4. **Before Commit**
   - `npm run type-check` - Verify types
   - `npm run lint` - Check code style
   - `npm run build` - Test production build
   - Run full API tests

## Next Steps

- [ ] Add authentication (JWT tokens)
- [ ] Implement rate limiting
- [ ] Add monitoring and alerting (Prometheus)
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Add video player enhancements
- [ ] Implement job retry logic
- [ ] Add download history tracking
- [ ] Setup email notifications
- [ ] Create admin dashboard
- [ ] Add multi-language support

## Support & Resources

- **API Documentation**: http://localhost:8080/docs (when Swagger enabled)
- **WebSocket Reference**: See `app/websocket/main.py`
- **React Hooks**: See `ui/src/hooks/useJobs.ts`
- **Type Definitions**: See `ui/src/types/index.ts`

---

**Last Updated**: February 15, 2026
**Status**: ✅ All Phases Complete - Ready for Deployment
