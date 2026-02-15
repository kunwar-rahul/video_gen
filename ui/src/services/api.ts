import axios, { AxiosError } from 'axios';
import {
  ApiResponse,
  VideoGenerationRequest,
  JobListResponse,
  JobResultResponse,
  JobFilters,
  PaginationParams
} from '@types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: any) => {
    // Add any auth tokens if needed
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: any) => response,
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export const jobsApi = {
  // Health check
  health: async (): Promise<ApiResponse<{ status: string }>> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Generate video
  generate: async (request: VideoGenerationRequest): Promise<ApiResponse<{ jobId: string }>> => {
    const response = await apiClient.post('/mcp/generate', request);
    return response.data;
  },

  // Get job status
  getStatus: async (jobId: string): Promise<ApiResponse<{ job: any }>> => {
    const response = await apiClient.get(`/mcp/status/${jobId}`);
    return response.data;
  },

  // List jobs with filters
  listJobs: async (
    filters?: JobFilters,
    pagination?: PaginationParams
  ): Promise<ApiResponse<JobListResponse>> => {
    const params: Record<string, any> = {};

    if (filters?.status) {
      params.status = Array.isArray(filters.status)
        ? filters.status.join(',')
        : filters.status;
    }

    if (filters?.priority) {
      params.priority = Array.isArray(filters.priority)
        ? filters.priority.join(',')
        : filters.priority;
    }

    if (filters?.dateRange) {
      params.date_range = filters.dateRange;
    }

    if (pagination?.limit) {
      params.limit = pagination.limit;
    }

    if (pagination?.offset) {
      params.offset = pagination.offset;
    }

    if (pagination?.sortBy) {
      params.sort_by = pagination.sortBy;
    }

    if (pagination?.sortOrder) {
      params.sort_order = pagination.sortOrder;
    }

    const response = await apiClient.get('/mcp/jobs', { params });
    return response.data;
  },

  // Get job result/video
  getResult: async (jobId: string): Promise<ApiResponse<JobResultResponse>> => {
    const response = await apiClient.get(`/mcp/result/${jobId}`);
    return response.data;
  },

  // Cancel job
  cancelJob: async (jobId: string): Promise<ApiResponse<{ success: boolean }>> => {
    const response = await apiClient.post(`/mcp/cancel/${jobId}`);
    return response.data;
  },

  // Get storyboard
  getStoryboard: async (jobId: string): Promise<ApiResponse<any>> => {
    const response = await apiClient.get(`/mcp/storyboard/${jobId}`);
    return response.data;
  },

  // Prefetch assets
  prefetchAssets: async (jobId: string): Promise<ApiResponse<{ success: boolean }>> => {
    const response = await apiClient.post(`/mcp/prefetch/${jobId}`);
    return response.data;
  }
};

export default apiClient;
