# Video Generation System - Quick Start

## TL;DR - Get Running in 3 Steps

### Step 1: Backend (Terminal 1)
```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start API + WebSocket servers
python run_all_services.py
```
✅ API running on `http://localhost:8080`  
✅ WebSocket on `ws://localhost:8085`

### Step 2: Frontend (Terminal 2)
```bash
cd ui

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```
✅ Frontend running on `http://localhost:3000`

### Step 3: Test (Terminal 3)
```bash
python test_api_comprehensive.py
```

---

## Full Setup Checklist

- [x] Python 3.10+ installed
- [x] Node.js 16+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Environment files configured (.env, .env.local)
- [x] Redis available (optional, for caching)
- [x] All services start without errors

Run validation:
```bash
python validate_system.py
```

---

## What's Running

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| API Server | 8080 | http://localhost:8080 | REST endpoints, job management |
| WebSocket | 8085 | ws://localhost:8085 | Real-time job updates |
| Frontend | 3000 | http://localhost:3000 | React UI |

---

## Key Features

### 📺 Video Generation
- Submit prompts → Get videos
- Track progress in real-time
- Download results when ready

### 🎛️ Job Management
- View all jobs in dashboard
- Filter by status, priority, date
- Cancel running jobs
- Download completed videos

### 📊 Analytics
- Success rates by priority
- Processing time tracking
- Queue depth monitoring
- Time series trends

### ⚙️ Settings
- Light/Dark theme
- Auto-refresh intervals
- Notification preferences

---

## API Examples

### Generate a Video
```bash
curl -X POST http://localhost:8080/mcp/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A sunset over the ocean",
    "duration_target": 30,
    "priority": 5
  }'
```

### List Jobs
```bash
curl http://localhost:8080/mcp/jobs?status=completed&limit=10
```

### Get Job Status
```bash
curl http://localhost:8080/mcp/status/YOUR_JOB_ID
```

---

## Frontend Development

### Type Checking
```bash
cd ui
npm run type-check
```

### Linting
```bash
cd ui
npm run lint
```

### Production Build
```bash
cd ui
npm run build
# Output in: ui/dist/
```

---

## Common Issues

### ❌ API Connection Refused
```bash
# Make sure backend is running
python run_all_services.py

# Check if port 8080 is available
lsof -i :8080
```

### ❌ WebSocket Not Connecting
- ✅ This is OK - app uses polling fallback
- Check browser console for details
- Verify `ws://localhost:8085` is accessible

### ❌ Frontend Build Fails
```bash
cd ui
rm -rf node_modules package-lock.json
npm install
npm run type-check
```

### ❌ Python Import Errors
```bash
pip install --upgrade -r requirements.txt
```

---

## Next Steps

1. ✅ Create video jobs
2. ✅ Monitor progress in dashboard
3. ✅ Download completed videos
4. ⬜ Configure Pexels API key (.env)
5. ⬜ Setup FFmpeg for rendering
6. ⬜ Deploy to production

---

## Documentation

For detailed information:
- **Setup & Testing**: `SETUP_AND_TESTING.md`
- **API Reference**: `docs/ARCHITECTURE.md`
- **Frontend Guide**: `ui/README.md`

---

**System Status**: ✅ Ready for Development

Run `python validate_system.py` to verify all components.
