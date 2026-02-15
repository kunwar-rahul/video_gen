import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Grid,
  Paper,
  Box,
  Typography,
  Button,
  Chip,
  LinearProgress,
  CircularProgress,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DownloadIcon from '@mui/icons-material/Download';
import { useJobDetails, useJobs } from '@hooks/useJobs';
import { JobStatus, Priority } from '@types';

const getStatusColor = (status: JobStatus) => {
  const colors: Record<JobStatus, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
    [JobStatus.QUEUED]: 'info',
    [JobStatus.PLANNING]: 'info',
    [JobStatus.RETRIEVING]: 'info',
    [JobStatus.GENERATING_AUDIO]: 'info',
    [JobStatus.RENDERING]: 'warning',
    [JobStatus.COMPLETED]: 'success',
    [JobStatus.FAILED]: 'error',
    [JobStatus.CANCELLED]: 'default'
  };
  return colors[status] || 'default';
};

const getPriorityColor = (priority: Priority) => {
  const colors: Record<Priority, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
    [Priority.LOW]: 'info',
    [Priority.MEDIUM]: 'primary',
    [Priority.HIGH]: 'warning',
    [Priority.CRITICAL]: 'error'
  };
  return colors[priority] || 'default';
};

const JobDetail = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const job = useJobDetails(jobId!);
  const { cancelJob } = useJobs();

  if (!job) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const handleCancel = async () => {
    try {
      await cancelJob(job.id);
      navigate('/jobs');
    } catch (error) {
      console.error('Failed to cancel job:', error);
    }
  };

  const isCompleted = job.status === JobStatus.COMPLETED;
  const isFailed = job.status === JobStatus.FAILED;
  const isProcessing = [JobStatus.PLANNING, JobStatus.RETRIEVING, JobStatus.GENERATING_AUDIO, JobStatus.RENDERING].includes(job.status);

  return (
    <Grid container spacing={3}>
      {/* Header */}
      <Grid item xs={12}>
        <Box display="flex" alignItems="center" gap={2}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/jobs')}
          >
            Back
          </Button>
          <Typography variant="h4">Job Details</Typography>
        </Box>
      </Grid>

      {/* Main Info */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Prompt
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {job.prompt}
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Progress
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Box flexGrow={1}>
                  <LinearProgress
                    variant="determinate"
                    value={job.progress.progress}
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
                <Typography variant="body2">{job.progress.progress}%</Typography>
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Current Stage
              </Typography>
              <Chip
                label={job.progress.currentStage}
                color={getStatusColor(job.progress.currentStage)}
              />
            </Grid>

            {/* Logs */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Logs
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', maxHeight: 200, overflow: 'auto' }}>
                {job.progress.logs && job.progress.logs.length > 0 ? (
                  <Box component="pre" sx={{ fontFamily: 'monospace', fontSize: '0.75rem', m: 0 }}>
                    {job.progress.logs.map((log: any, idx: number) => (
                      <div key={idx}>{log}</div>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    No logs available
                  </Typography>
                )}
              </Paper>
            </Grid>

            {isCompleted && job.resultUrl && (
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Result Video
                </Typography>
                <video
                  controls
                  src={job.resultUrl}
                  style={{ maxWidth: '100%', borderRadius: 8 }}
                />
              </Grid>
            )}
          </Grid>
        </Paper>
      </Grid>

      {/* Sidebar Info */}
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Job Information
          </Typography>

          <Box display="flex" flexDirection="column" gap={2}>
            <Box>
              <Typography variant="caption" color="textSecondary">
                Status
              </Typography>
              <Chip
                label={job.status}
                color={getStatusColor(job.status)}
              />
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                Priority
              </Typography>
              <Chip
                label={job.priority}
                color={getPriorityColor(job.priority)}
                variant="outlined"
              />
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                Job ID
              </Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                {job.id}
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                Created
              </Typography>
              <Typography variant="body2">
                {new Date(job.createdAt).toLocaleString()}
              </Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                Updated
              </Typography>
              <Typography variant="body2">
                {new Date(job.updatedAt).toLocaleString()}
              </Typography>
            </Box>

            {job.completedAt && (
              <Box>
                <Typography variant="caption" color="textSecondary">
                  Completed
                </Typography>
                <Typography variant="body2">
                  {new Date(job.completedAt).toLocaleString()}
                </Typography>
              </Box>
            )}

            {isFailed && job.errorMessage && (
              <Box>
                <Typography variant="caption" color="error">
                  Error Message
                </Typography>
                <Typography variant="body2" color="error">
                  {job.errorMessage}
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>

        {/* Actions */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Actions
          </Typography>
          <Box display="flex" flexDirection="column" gap={1}>
            {isCompleted && job.resultUrl && (
              <>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                >
                  Play
                </Button>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                >
                  Download
                </Button>
              </>
            )}

            {isProcessing && (
              <Button
                fullWidth
                variant="contained"
                color="error"
                onClick={handleCancel}
              >
                Cancel Job
              </Button>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default JobDetail;
