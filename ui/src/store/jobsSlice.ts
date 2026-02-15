import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { VideoJob, JobStatus, Priority } from '@types';

interface JobsState {
  jobs: VideoJob[];
  selectedJobId: string | null;
  total: number;
  pages: number;
  currentPage: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  filters: {
    status?: JobStatus;
    priority?: Priority;
    dateRange?: string;
    search?: string;
  };
  summary: {
    total: number;
    queued: number;
    processing: number;
    completed: number;
    failed: number;
  };
}

const initialState: JobsState = {
  jobs: [],
  selectedJobId: null,
  total: 0,
  pages: 0,
  currentPage: 1,
  pageSize: 10,
  loading: false,
  error: null,
  filters: {},
  summary: {
    total: 0,
    queued: 0,
    processing: 0,
    completed: 0,
    failed: 0
  }
};

const jobsSlice = createSlice({
  name: 'jobs',
  initialState,
  reducers: {
    setJobsLoading(state: JobsState, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setJobsError(state: JobsState, action: PayloadAction<string | null>) {
      state.error = action.payload;
      state.loading = false;
    },
    setJobs(state: JobsState, action: PayloadAction<{
      jobs: VideoJob[];
      total: number;
      pages: number;
      currentPage: number;
      pageSize: number;
      summary: any;
    }>) {
      const { jobs, total, pages, currentPage, pageSize, summary } = action.payload;
      state.jobs = jobs;
      state.total = total;
      state.pages = pages;
      state.currentPage = currentPage;
      state.pageSize = pageSize;
      state.summary = summary;
      state.loading = false;
    },
    setSelectedJobId(state: JobsState, action: PayloadAction<string | null>) {
      state.selectedJobId = action.payload;
    },
    updateJobStatus(state: JobsState, action: PayloadAction<{ jobId: string; status: JobStatus; progress: number }>) {
      const { jobId, status, progress } = action.payload;
      const job = state.jobs.find((j: VideoJob) => j.id === jobId);
      if (job) {
        job.status = status;
        job.progress.progress = progress;
        job.progress.currentStage = status;
      }
    },
    addJobLog(state: JobsState, action: PayloadAction<{ jobId: string; message: string }>) {
      const { jobId, message } = action.payload;
      const job = state.jobs.find((j: VideoJob) => j.id === jobId);
      if (job && job.progress.logs) {
        job.progress.logs.push(message);
      }
    },
    setFilters(state: JobsState, action: PayloadAction<any>) {
      state.filters = action.payload;
      state.currentPage = 1;
    },
    setCurrentPage(state: JobsState, action: PayloadAction<number>) {
      state.currentPage = action.payload;
    },
    setPageSize(state: JobsState, action: PayloadAction<number>) {
      state.pageSize = action.payload;
      state.currentPage = 1;
    }
  }
});

export const {
  setJobsLoading,
  setJobsError,
  setJobs,
  setSelectedJobId,
  updateJobStatus,
  addJobLog,
  setFilters,
  setCurrentPage,
  setPageSize
} = jobsSlice.actions;

export default jobsSlice.reducer;
