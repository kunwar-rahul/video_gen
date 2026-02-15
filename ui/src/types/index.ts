// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Job Status Types
export enum JobStatus {
  QUEUED = 'queued',
  PLANNING = 'planning',
  RETRIEVING = 'retrieving',
  GENERATING_AUDIO = 'generating_audio',
  RENDERING = 'rendering',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// Job Related Types
export interface VideoGenerationRequest {
  prompt: string;
  style?: string;
  duration?: number;
  voiceId?: string;
  priority?: Priority;
  metadata?: Record<string, any>;
}

export interface Scene {
  id: string;
  description: string;
  duration: number;
  order: number;
  timestamps: {
    start: number;
    end: number;
  };
}

export interface Storyboard {
  id: string;
  scenes: Scene[];
  duration: number;
  aspectRatio: string;
  generatedAt: string;
}

export interface JobProgress {
  currentStage: JobStatus;
  progress: number;
  completedAt?: string;
  startedAt: string;
  estimatedTimeRemaining?: number;
  logs?: string[];
}

export interface VideoJob {
  id: string;
  status: JobStatus;
  prompt: string;
  priority: Priority;
  progress: JobProgress;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  duration?: number;
  resultUrl?: string;
  storyboardId?: string;
  errorMessage?: string;
}

export interface JobListResponse {
  jobs: VideoJob[];
  total: number;
  pages: number;
  currentPage: number;
  pageSize: number;
  summary: {
    total: number;
    queued: number;
    processing: number;
    completed: number;
    failed: number;
  };
}

export interface JobDetailResponse {
  job: VideoJob;
  storyboard?: Storyboard;
  logs?: Array<{
    timestamp: string;
    level: string;
    message: string;
  }>;
}

export interface JobResultResponse {
  jobId: string;
  status: JobStatus;
  videoUrl: string;
  duration: number;
  fileSize: number;
  metadata: Record<string, any>;
}

// WebSocket Event Types
export interface WebSocketEvent {
  type: string;
  payload: any;
  timestamp: string;
}

export interface JobStatusUpdateEvent extends WebSocketEvent {
  type: 'job_status_update';
  payload: {
    jobId: string;
    status: JobStatus;
    progress: number;
  };
}

export interface JobLogEntryEvent extends WebSocketEvent {
  type: 'job_log_entry';
  payload: {
    jobId: string;
    level: string;
    message: string;
  };
}

export interface JobCompletedEvent extends WebSocketEvent {
  type: 'job_completed';
  payload: {
    jobId: string;
    videoUrl: string;
    duration: number;
  };
}

export interface JobFailedEvent extends WebSocketEvent {
  type: 'job_failed';
  payload: {
    jobId: string;
    errorMessage: string;
  };
}

// Pagination
export interface PaginationParams {
  limit: number;
  offset: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Filters
export interface JobFilters {
  status?: JobStatus | JobStatus[];
  priority?: Priority | Priority[];
  dateRange?: 'today' | 'week' | 'month' | 'all';
  search?: string;
}

// Dashboard Stats
export interface DashboardStats {
  totalJobs: number;
  completedToday: number;
  failedToday: number;
  averageRenderTime: number;
  queueDepth: number;
  successRate: number;
  totalStorage: number;
}

// Theme
export type ThemeMode = 'light' | 'dark';
