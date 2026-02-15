import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@store';
import {
  setJobsLoading,
  setJobsError,
  setJobs,
  setSelectedJobId,
  updateJobStatus,
  addJobLog
} from '@store/jobsSlice';
import { jobsApi } from '@services/api';
import webSocketService from '@services/websocket';
import { JobFilters } from '@types';

export const useJobs = () => {
  const dispatch = useDispatch<AppDispatch>();
  const jobs = useSelector((state: RootState) => state.jobs);

  const fetchJobs = useCallback(async (filters?: JobFilters) => {
    dispatch(setJobsLoading(true));
    try {
      const pagination = {
        limit: jobs.pageSize,
        offset: (jobs.currentPage - 1) * jobs.pageSize
      };

      const response = await jobsApi.listJobs(filters, pagination);

      if (response.data) {
        dispatch(setJobs(response.data));
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to fetch jobs';
      dispatch(setJobsError(errorMessage));
    }
  }, [dispatch, jobs.currentPage, jobs.pageSize]);

  const generateVideo = useCallback(async (prompt: string, priority?: string) => {
    dispatch(setJobsLoading(true));
    try {
      const response = await jobsApi.generate({
        prompt,
        priority: priority as any
      });
      if (response.data?.jobId) {
        await fetchJobs();
        return response.data.jobId;
      }
    } catch (error: any) {
      dispatch(setJobsError(error.message));
      throw error;
    }
  }, [dispatch, fetchJobs]);

  const cancelJob = useCallback(async (jobId: string) => {
    try {
      await jobsApi.cancelJob(jobId);
      await fetchJobs();
    } catch (error: any) {
      dispatch(setJobsError(error.message));
      throw error;
    }
  }, [dispatch, fetchJobs]);

  return {
    ...jobs,
    fetchJobs,
    generateVideo,
    cancelJob
  };
};

export const useJobDetails = (jobId: string | null) => {
  const dispatch = useDispatch<AppDispatch>();
  const selectedJobId = useSelector((state: RootState) => state.jobs.selectedJobId);
  const job = useSelector((state: RootState) =>
    state.jobs.jobs.find((j: any) => j.id === jobId || j.id === selectedJobId)
  );

  useEffect(() => {
    if (jobId) {
      dispatch(setSelectedJobId(jobId));
      webSocketService.subscribeToJob(jobId);

      return () => {
        webSocketService.unsubscribeFromJob(jobId);
      };
    }
  }, [jobId, dispatch]);

  useEffect(() => {
    const handleStatusUpdate = (event: any) => {
      if (event.payload.jobId === jobId) {
        dispatch(updateJobStatus({
          jobId: event.payload.jobId,
          status: event.payload.status,
          progress: event.payload.progress
        }));
      }
    };

    const handleLogEntry = (event: any) => {
      if (event.payload.jobId === jobId) {
        dispatch(addJobLog({
          jobId: event.payload.jobId,
          message: event.payload.message
        }));
      }
    };

    webSocketService.on('job_status_update', handleStatusUpdate);
    webSocketService.on('job_log_entry', handleLogEntry);

    return () => {
      webSocketService.off('job_status_update', handleStatusUpdate);
      webSocketService.off('job_log_entry', handleLogEntry);
    };
  }, [jobId, dispatch]);

  return job;
};

export const useWebSocket = () => {
  useEffect(() => {
    const connect = async () => {
      try {
        await webSocketService.connect();
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connect();

    return () => {
      webSocketService.disconnect();
    };
  }, []);

  return webSocketService;
};

export const useNotification = () => {
  return useCallback((message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    // This would typically dispatch to UI slice
    console.log(`[${type}] ${message}`);
  }, []);
};
