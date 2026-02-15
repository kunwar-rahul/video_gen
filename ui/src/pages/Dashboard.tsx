import { useEffect } from 'react';
import { Grid, Paper, Box, Typography, Card, CardContent, CircularProgress, Alert, Button } from '@mui/material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useJobs } from '@hooks/useJobs';

const Dashboard = () => {
  const { jobs, summary, loading, fetchJobs, error } = useJobs();

  useEffect(() => {
    // Fetch once on mount; rely on WebSocket for live updates instead of polling
    fetchJobs();
  }, [fetchJobs]);

  if (loading && jobs.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error && jobs.length === 0) {
    return (
      <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center" minHeight="400px" sx={{ p: 2 }}>
        <Alert severity="error" sx={{ mb: 2, width: '100%', maxWidth: 600 }}>{error}</Alert>
        <Button variant="contained" onClick={() => fetchJobs()}>Retry</Button>
      </Box>
    );
  }

  const statusData = [
    { name: 'Queued', value: summary.queued, fill: '#2196f3' },
    { name: 'Processing', value: summary.processing, fill: '#ff9800' },
    { name: 'Completed', value: summary.completed, fill: '#4caf50' },
    { name: 'Failed', value: summary.failed, fill: '#f44336' }
  ];

  const recentJobs = jobs.slice(0, 5).map((job: any) => ({
    name: job.prompt.substring(0, 20) + '...',
    progress: job.progress.progress,
    status: job.status
  }));

  const stats = [
    { label: 'Total Jobs', value: summary.total },
    { label: 'Queued', value: summary.queued },
    { label: 'Processing', value: summary.processing },
    { label: 'Completed', value: summary.completed },
    { label: 'Failed', value: summary.failed }
  ];

  return (
    <Grid container spacing={3}>
      {/* Key Metrics */}
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
      </Grid>

      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={4} lg={2.4} key={index}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                {stat.label}
              </Typography>
              <Typography variant="h5">
                {stat.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Status Distribution */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Job Status Distribution
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Recent Jobs Progress */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Jobs Progress
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={recentJobs}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="progress" fill="#1976d2" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Recent Activity */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Recent Jobs
          </Typography>
          <Box sx={{ overflowX: 'auto' }}>
            {jobs.slice(0, 5).map((job: any) => (
              <Box key={job.id} sx={{ p: 1, mb: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="body2" noWrap>
                  {job.prompt}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Status: {job.status} | Progress: {job.progress.progress}%
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Dashboard;
