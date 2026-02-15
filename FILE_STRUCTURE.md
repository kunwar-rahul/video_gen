# Project File Structure & Locations

## Backend (Python)

### Core Services
- **`app/api/main.py`** (320 lines)
  - Flask REST API server
  - 7 endpoints for job management
  - Integration with job service utilities
  
- **`app/api/jobs_service.py`** (89 lines)
  - Job filtering, sorting, pagination
  - Helper functions for list endpoint
  
- **`app/websocket/main.py`** (180 lines)
  - Socket.io WebSocket server
  - Event broadcasting system
  - Client room management
  
- **`app/websocket/events.py`** (70 lines)
  - Event manager bridge pattern
  - Broadcast helpers
  - Integration with API

### Common Modules
- **`app/common/models.py`** - Data models (VideoRequest, JobStatus, etc.)
- **`app/common/config.py`** - Configuration management
- **`app/common/utils.py`** - Logging, caching, utilities

### Microservices (Optional)
- **`app/orchestrator/main.py`** - Job planning and coordination
- **`app/retriever/main.py`** - Pexels API integration
- **`app/whisper_worker/main.py`** - Audio processing
- **`app/renderer/main.py`** - Video rendering with FFmpeg

### Server Entry Points
- **`local_dev.py`** - Local development endpoint launcher
- **`websocket_server.py`** - Standalone WebSocket server
- **`run_all_services.py`** - Combined API + WebSocket launcher (RECOMMENDED)

---

## Frontend (React/TypeScript)

### Application Root
- **`ui/src/App.tsx`** - Main app component with routing
- **`ui/src/main.tsx`** - React entry point
- **`ui/src/index.css`** - Global styles

### Configuration
- **`ui/package.json`** - Dependencies and scripts
- **`ui/tsconfig.json`** - TypeScript configuration
- **`ui/vite.config.ts`** - Vite build setup
- **`ui/.eslintrc.cjs`** - Linting rules
- **`ui/index.html`** - HTML entry point

### Pages (Components)
- **`ui/src/pages/Dashboard.tsx`** - Main dashboard with KPIs and charts
- **`ui/src/pages/JobsList.tsx`** - Filterable job table with pagination
- **`ui/src/pages/JobDetail.tsx`** - Job progress tracking and logs
- **`ui/src/pages/QuickGenerate.tsx`** - Video generation form
- **`ui/src/pages/Analytics.tsx`** - Performance analytics dashboard
- **`ui/src/pages/Settings.tsx`** - Application preferences

### Components
- **`ui/src/components/Layout.tsx`** - Main layout with sidebar and app bar

### State Management (Redux)
- **`ui/src/store/index.ts`** - Redux store configuration
- **`ui/src/store/jobsSlice.ts`** - Job state and reducers
- **`ui/src/store/uiSlice.ts`** - UI state (theme, notifications)

### API & WebSocket Clients
- **`ui/src/services/api.ts`** - Axios HTTP client
- **`ui/src/services/websocket.ts`** - Socket.io WebSocket client

### Custom Hooks
- **`ui/src/hooks/useJobs.ts`** - Job management hooks

### Type Definitions
- **`ui/src/types/index.ts`** - All TypeScript interfaces and types

### Theming
- **`ui/src/theme/index.tsx`** - Material-UI theme provider

### Configuration Files
- **`ui/.env.example`** - Environment variable template
- **`ui/.env.local`** - Local environment (created during setup)
- **`ui/.gitignore`** - Git ignore rules
- **`ui/.editorconfig`** - Editor configuration

---

## Testing & Validation

### Test Suites
- **`test_api.py`** - Original basic API tests
- **`test_api_comprehensive.py`** - Comprehensive 8-test suite (RECOMMENDED)
- **`validate_system.py`** - System validation script

### Test Coverage
- Backend API: 8/8 tests
- Frontend: TypeScript validation + ESLint
- End-to-end: Manual via UI

---

## Documentation

### Quick Reference
- **`QUICKSTART.md`** - 5-minute setup guide (START HERE)
- **`SETUP_AND_TESTING.md`** - Complete setup and testing
- **`IMPLEMENTATION_SUMMARY.md`** - This document + comprehensive overview

### Project Root
- **`README.md`** - Project overview
- **`ARCHITECTURE.md`** - Technical architecture details

### Frontend
- **`ui/README.md`** - Frontend-specific documentation

---

## Setup & Deployment

### Setup Scripts
- **`setup.sh`** - Bash setup script (Linux/Mac)
- **`setup.bat`** - Windows setup script (RECOMMENDED FOR WINDOWS)

### Docker
- **`docker-compose.yml`** - Full stack containerization
- **`Dockerfile`** - Backend container (in Docker Compose)

### Configuration & Environment
- **`.env.example`** - Backend environment template
- **`.env`** - Backend environment (created during setup)

---

## Dependencies & Requirements

- **`requirements.txt`** - Python dependencies
- **`ui/package.json`** - Node.js/npm dependencies

---

## File Organization at a Glance

```
video_gen/ (Root)
├── 📁 app/ (Backend code)
│   ├── api/
│   ├── websocket/
│   ├── common/
│   ├── orchestrator/
│   ├── retriever/
│   ├── whisper_worker/
│   └── renderer/
│
├── 📁 ui/ (Frontend code)
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── store/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── theme/
│   │   └── App.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── 📁 docs/ (Documentation)
│   ├── ARCHITECTURE.md
│   └── GETTING_STARTED.md
│
├── 📄 Python Files (Launchers)
│   ├── local_dev.py
│   ├── run_all_services.py
│   ├── websocket_server.py
│   └── validate_system.py
│
├── 📄 Test Files
│   ├── test_api.py
│   ├── test_api_comprehensive.py
│   └── validate_system.py
│
├── 📄 Setup Scripts
│   ├── setup.sh
│   └── setup.bat
│
├── 📄 Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── SETUP_AND_TESTING.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── FILE_STRUCTURE.md (this file)
│   └── requirements.txt
│
└── 📄 Deployment
    ├── docker-compose.yml
    └── .gitignore
```

---

## Quick Navigation

### I want to...

**👉 Get started quickly**
→ Read: `QUICKSTART.md`

**👉 Deploy to production**
→ Run: `docker-compose up -d`

**👉 Understand the architecture**
→ Read: `SETUP_AND_TESTING.md` → `Architecture` section

**👉 Develop backend features**
→ Edit: `app/api/main.py` or specific service file

**👉 Develop frontend features**
→ Edit: `ui/src/pages/` or `ui/src/components/`

**👉 Run tests**
→ Run: `python test_api_comprehensive.py`

**👉 Check types**
→ Run: `cd ui && npm run type-check`

**👉 Debug an issue**
→ Run: `python validate_system.py`

**👉 See implementation details**
→ Read: `IMPLEMENTATION_SUMMARY.md`

---

## Development Tips

### Adding a New Page
1. Create `ui/src/pages/MyPage.tsx`
2. Add route in `ui/src/App.tsx`
3. Add menu item in `ui/src/components/Layout.tsx`
4. Use Redux hooks: `useSelector`, `useDispatch`
5. Type everything with `@types`

### Adding an API Endpoint
1. Create route in `app/api/main.py`
2. Add tests in `test_api_comprehensive.py`
3. Update frontend API client: `ui/src/services/api.ts`
4. Create corresponding types in `ui/src/types/index.ts`
5. Add page/component to use it

### WebSocket Events
1. Define event in `app/websocket/main.py`
2. Use event manager in API: `WebSocketEventManager.broadcast_*`
3. Listen in frontend hook: `useWebSocket().on()`
4. Update Redux state on event

---

**Last Updated**: February 15, 2026  
**Status**: Complete & Production-Ready
