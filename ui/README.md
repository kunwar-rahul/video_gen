# Video Generation UI

React-based web interface for managing and monitoring video generation jobs.

## Features

- **Dashboard**: Real-time overview of job statistics and recent activities
- **Jobs Management**: View, filter, sort, and manage all video generation jobs
- **Job Details**: Monitor job progress with logs, storyboards, and result videos
- **Quick Generate**: Simplified form for creating new video generation jobs
- **Analytics**: Comprehensive analytics and performance metrics
- **Settings**: Configurable application preferences
- **Real-time Updates**: WebSocket integration for live job status updates
- **Responsive Design**: Mobile-friendly interface with Material-UI

## Tech Stack

- **React 18**: UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Redux Toolkit**: State management
- **Material-UI (MUI)**: Component library
- **Socket.io**: Real-time communication
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **React Router**: Client-side routing
- **Formik + Yup**: Form management and validation

## Project Structure

```
src/
├── components/        # Reusable UI components
│   └── Layout.tsx    # Main layout wrapper
├── pages/            # Page components
│   ├── Dashboard.tsx
│   ├── JobsList.tsx
│   ├── JobDetail.tsx
│   ├── QuickGenerate.tsx
│   ├── Analytics.tsx
│   └── Settings.tsx
├── services/         # API and WebSocket services
│   ├── api.ts       # REST API client
│   └── websocket.ts # WebSocket client
├── store/           # Redux store configuration
│   ├── index.ts     # Store setup
│   ├── jobsSlice.ts # Jobs state
│   └── uiSlice.ts   # UI state
├── hooks/           # Custom React hooks
│   └── useJobs.ts   # Job management hooks
├── types/           # TypeScript type definitions
│   └── index.ts
├── theme/           # Material-UI theme
│   └── index.tsx
├── App.tsx          # Root app component
├── main.tsx         # React entry point
└── index.css        # Global styles
```

## Installation

### Prerequisites

- Node.js 16+ and npm/yarn
- Running backend API server on `localhost:8080`
- WebSocket server on `localhost:8085` (optional, app works with polling)

### Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local to match your backend URLs
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```
   App will be available at `http://localhost:3000`

## Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### Build Configuration

The app uses Vite for fast, optimized builds. Key configurations:

- **API Proxy**: Dev server proxies `/api` requests to `http://localhost:8080`
- **Path Aliases**: Import shortcuts using `@` prefix (e.g., `@components`, `@services`)
- **Target**: ES2020 with full support for modern JavaScript features

## API Integration

The app connects to the backend via:

### REST API
- Base URL: `http://localhost:8080`
- Endpoints: Health check, job CRUD, video generation, results

### WebSocket (Real-time)
- URL: `http://localhost:8085`
- Events: Job status updates, logs, completion/failure notifications

See [api.ts](src/services/api.ts) and [websocket.ts](src/services/websocket.ts) for details.

## State Management

Redux Toolkit is used for state management:

- **jobsSlice**: Manages jobs list, filters, pagination, selected job
- **uiSlice**: Manages theme, sidebar state, notifications

Access state using Redux hooks:
```typescript
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '@store';

const jobs = useSelector((state: RootState) => state.jobs.jobs);
const dispatch = useDispatch<AppDispatch>();
```

## Custom Hooks

### useJobs()
Provides job management functionality:
```typescript
const { jobs, fetchJobs, generateVideo, cancelJob, loading, error } = useJobs();
```

### useJobDetails(jobId)
Subscribes to real-time updates for a specific job:
```typescript
const job = useJobDetails(jobId);
```

### useWebSocket()
Low-level WebSocket access:
```typescript
const ws = useWebSocket();
ws.on('job_status_update', (event) => { /* ... */ });
```

## Styling

Material-UI is used for styling with a custom theme:
- **Light/Dark Modes**: Toggle via theme button in AppBar
- **Responsive**: Mobile-first design with breakpoints
- **Customizable**: Theme configuration in [theme/index.tsx](src/theme/index.tsx)

## Type Safety

Comprehensive TypeScript types for:
- API requests/responses
- WebSocket events
- Redux state
- React props

See [types/index.ts](src/types/index.ts) for all types.

## Performance

- **Lazy Loading**: Pages loaded on demand
- **Code Splitting**: Automatic with Vite
- **Image Optimization**: Vite handles asset optimization
- **Caching**: Redux persists state in memory

## Deployment

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory, ready for deployment to any static hosting.

### Environment Configuration

Create `.env.production` for production URLs:
```
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=https://ws.yourdomain.com
```

## Troubleshooting

### API Connection Issues
- Check that backend API is running on configured URL
- Verify CORS settings on backend
- Check browser console for network errors

### WebSocket Connection Issues
- WebSocket is optional; app falls back to polling
- Check that WebSocket server is running
- Verify firewall/network allows connections

### Build Issues
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf .vite`
- Check TypeScript errors: `npm run type-check`

## Contributing

- Follow TypeScript/React best practices
- Use type safety; avoid `any` types
- Keep components small and focused
- Add PropTypes/JSDoc for complex props
- Test API changes with real backend

## License

Same as main project.
