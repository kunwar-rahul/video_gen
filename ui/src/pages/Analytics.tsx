import { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useJobs } from '@hooks/useJobs';
import { JobStatus } from '@types';

const Analytics = () => {
  const { jobs, summary } = useJobs();
  const [timeRange, setTimeRange] = useState('week');

  // Generate mock analytics data
  const generateTimeSeriesData = () => {
    const data = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        completed: Math.floor(Math.random() * 50) + 10,
        failed: Math.floor(Math.random() * 10) + 2,
        processing: Math.floor(Math.random() * 30) + 5
      });
    }
    return data;
  };

  const timeSeriesData = generateTimeSeriesData();

  // Performance metrics
  const performanceData = [
    { name: 'Scene Planning', time: 12, fill: '#8884d8' },
    { name: 'Asset Retrieval', time: 25, fill: '#82ca9d' },
    { name: 'Audio Generation', time: 18, fill: '#ffc658' },
    { name: 'Rendering', time: 45, fill: '#ff7c7c' }
  ];

  // Success rate by priority
  const priorityData = [
    { name: 'Critical', value: 95, fill: '#ff7c7c' },
    { name: 'High', value: 88, fill: '#ffc658' },
    { name: 'Medium', value: 92, fill: '#82ca9d' },
    { name: 'Low', value: 85, fill: '#8884d8' }
  ];

  // Stats cards
  const stats = [
    {
      label: 'Success Rate',
      value: `${Math.round((summary.completed / summary.total) * 100) || 0}%`,
      color: '#4caf50'
    },
    {
      label: 'Avg. Render Time',
      value: '2m 15s',
      color: '#2196f3'
    },
    {
      label: 'Queue Depth',
      value: summary.queued,
      color: '#ff9800'
    },
    {
      label: 'Total Storage',
      value: '124 GB',
      color: '#9c27b0'
    }
  ];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4">Analytics</Typography>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="week">Last 7 Days</MenuItem>
              <MenuItem value="month">Last 30 Days</MenuItem>
              <MenuItem value="quarter">Last 90 Days</MenuItem>
              <MenuItem value="year">Last Year</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Grid>

      {/* Stats Cards */}
      {stats.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                {stat.label}
              </Typography>
              <Typography variant="h5" sx={{ color: stat.color }}>
                {stat.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Job Status Over Time */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Job Status Trend
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="completed" stackId="1" stroke="#4caf50" fill="#4caf50" />
              <Area type="monotone" dataKey="processing" stackId="1" stroke="#ff9800" fill="#ff9800" />
              <Area type="monotone" dataKey="failed" stackId="1" stroke="#f44336" fill="#f44336" />
            </AreaChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Success Rate by Priority */}
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Success Rate by Priority
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={priorityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {priorityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value}%`} />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Processing Time by Stage */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Avg. Processing Time by Stage
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis label={{ value: 'Seconds', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => `${value}s`} />
              <Bar dataKey="time" fill="#1976d2" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      {/* Job Summary */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Summary Statistics
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Total Jobs
                </Typography>
                <Typography variant="h6">{summary.total}</Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Completed
                </Typography>
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  {summary.completed}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Processing
                </Typography>
                <Typography variant="h6" sx={{ color: '#ff9800' }}>
                  {summary.processing}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Failed
                </Typography>
                <Typography variant="h6" sx={{ color: '#f44336' }}>
                  {summary.failed}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default Analytics;
