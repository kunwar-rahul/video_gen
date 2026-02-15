import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@store';
import { ThemeProvider } from '@theme';
import Layout from '@components/Layout';
import Dashboard from '@pages/Dashboard';
import JobsList from '@pages/JobsList';
import JobDetail from '@pages/JobDetail';
import QuickGenerate from '@pages/QuickGenerate';
import Analytics from '@pages/Analytics';
import Settings from '@pages/Settings';
import webSocketService from '@services/websocket';

const AppContent = () => {
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    webSocketService.connect().catch(err => {
      console.warn('WebSocket connection failed, app will work in polling mode:', err);
    });

    return () => {
      webSocketService.disconnect();
    };
  }, []);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<JobsList />} />
          <Route path="/jobs/:jobId" element={<JobDetail />} />
          <Route path="/generate" element={<QuickGenerate />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Box>
  );
};

const App = () => {
  return (
    <Router>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </Router>
  );
};

export default App;
