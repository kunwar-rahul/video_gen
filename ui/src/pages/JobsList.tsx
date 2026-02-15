import { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Box,
  Chip,
  CircularProgress,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { useJobs } from '@hooks/useJobs';
import { setCurrentPage, setPageSize, setFilters } from '@store/jobsSlice';
import { JobStatus, Priority } from '@types';
import { AppDispatch } from '@store';

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

const JobsList = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const {
    jobs,
    total,
    pages,
    currentPage,
    pageSize,
    loading,
    fetchJobs,
    summary
  } = useJobs();

  const [filters, setLocalFilters] = useState({
    status: '',
    priority: '',
    dateRange: 'all'
  });

  useEffect(() => {
    const jobFilters: any = {
      ...(filters.status && { status: filters.status }),
      ...(filters.priority && { priority: filters.priority }),
      ...(filters.dateRange && { dateRange: filters.dateRange })
    };
    fetchJobs(jobFilters);
  }, [currentPage, pageSize, filters, fetchJobs]);

  const handleFilterChange = (event: any) => {
    const { name, value } = event.target;
    const newFilters = { ...filters, [name]: value };
    setLocalFilters(newFilters);
    dispatch(setCurrentPage(1));
    dispatch(setFilters(newFilters));
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    dispatch(setCurrentPage(newPage + 1));
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(setPageSize(parseInt(event.target.value, 10)));
    dispatch(setCurrentPage(1));
  };

  const handleJobClick = (jobId: string) => {
    navigate(`/jobs/${jobId}`);
  };

  if (loading && jobs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Jobs
        </Typography>
      </Grid>

      {/* Filters */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Box display="flex" gap={2} flexWrap="wrap">
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Status</InputLabel>
              <Select
                name="status"
                value={filters.status}
                onChange={handleFilterChange}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                {Object.values(JobStatus).map((status: any) => (
                  <MenuItem key={String(status)} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={filters.priority}
                onChange={handleFilterChange}
                label="Priority"
              >
                <MenuItem value="">All</MenuItem>
                {Object.values(Priority).map((priority: any) => (
                  <MenuItem key={String(priority)} value={priority}>
                    {String(priority)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Date Range</InputLabel>
              <Select
                name="dateRange"
                value={filters.dateRange}
                onChange={handleFilterChange}
                label="Date Range"
              >
                <MenuItem value="today">Today</MenuItem>
                <MenuItem value="week">This Week</MenuItem>
                <MenuItem value="month">This Month</MenuItem>
                <MenuItem value="all">All Time</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Paper>
      </Grid>

      {/* Summary Stats */}
      <Grid item xs={12}>
        <Box display="flex" gap={2} flexWrap="wrap">
          <Chip label={`Total: ${summary.total}`} />
          <Chip label={`Queued: ${summary.queued}`} color="info" variant="outlined" />
          <Chip label={`Processing: ${summary.processing}`} color="warning" variant="outlined" />
          <Chip label={`Completed: ${summary.completed}`} color="success" variant="outlined" />
          <Chip label={`Failed: ${summary.failed}`} color="error" variant="outlined" />
        </Box>
      </Grid>

      {/* Jobs Table */}
      <Grid item xs={12}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'action.hover' }}>
                <TableCell>Prompt</TableCell>
                <TableCell align="center">Status</TableCell>
                <TableCell align="center">Priority</TableCell>
                <TableCell align="right">Progress</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {jobs.map((job: any) => (
                <TableRow key={job.id} hover>
                  <TableCell>{job.prompt.substring(0, 50)}...</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={job.status}
                      color={getStatusColor(job.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={job.priority}
                      color={getPriorityColor(job.priority)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">{job.progress.progress}%</TableCell>
                  <TableCell>{new Date(job.createdAt).toLocaleDateString()}</TableCell>
                  <TableCell align="center">
                    <Button
                      size="small"
                      onClick={() => handleJobClick(job.id)}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={total}
            rowsPerPage={pageSize}
            page={currentPage - 1}
            onPageChange={handlePageChange}
            onRowsPerPageChange={handleRowsPerPageChange}
          />
        </TableContainer>
      </Grid>
    </Grid>
  );
};

export default JobsList;
