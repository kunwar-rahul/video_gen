import { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@store';
import { setTheme } from '@store/uiSlice';

const Settings = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { themeMode } = useSelector((state: RootState) => state.ui);
  const [saved, setSaved] = useState(false);

  const [settings, setSettings] = useState({
    theme: themeMode,
    autoRefresh: true,
    refreshInterval: 30,
    notifications: true,
    soundNotifications: false,
    emailNotifications: false,
    apiKey: '••••••••••••••••',
    showLogs: true
  });

  const handleSettingChange = (e: any) => {
    const target = e.target as any;
    const { name, value, type, checked } = target;
    setSettings(prev => ({
      ...prev,
      [name!]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = () => {
    if (settings.theme !== themeMode) {
      dispatch(setTheme(settings.theme as 'light' | 'dark'));
    }
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Grid container spacing={3} maxWidth="900px">
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
      </Grid>

      {saved && (
        <Grid item xs={12}>
          <Alert severity="success">Settings saved successfully!</Alert>
        </Grid>
      )}

      {/* Display Settings */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Display Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box display="flex" flexDirection="column" gap={2}>
            <FormControl>
              <InputLabel>Theme</InputLabel>
              <Select
                name="theme"
                value={settings.theme}
                onChange={handleSettingChange}
                label="Theme"
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  name="showLogs"
                  checked={settings.showLogs}
                  onChange={handleSettingChange}
                />
              }
              label="Show Job Logs"
            />
          </Box>
        </Paper>
      </Grid>

      {/* Auto-Refresh Settings */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Auto-Refresh Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box display="flex" flexDirection="column" gap={2}>
            <FormControlLabel
              control={
                <Switch
                  name="autoRefresh"
                  checked={settings.autoRefresh}
                  onChange={handleSettingChange}
                />
              }
              label="Enable Auto-Refresh"
            />

            {settings.autoRefresh && (
              <TextField
                name="refreshInterval"
                label="Refresh Interval (seconds)"
                type="number"
                value={settings.refreshInterval}
                onChange={handleSettingChange}
                inputProps={{ min: 5, max: 300, step: 5 }}
                helperText="How often to update job status"
              />
            )}
          </Box>
        </Paper>
      </Grid>

      {/* Notification Settings */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Notification Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box display="flex" flexDirection="column" gap={2}>
            <FormControlLabel
              control={
                <Switch
                  name="notifications"
                  checked={settings.notifications}
                  onChange={handleSettingChange}
                />
              }
              label="Enable Notifications"
            />

            {settings.notifications && (
              <>
                <FormControlLabel
                  control={
                    <Switch
                      name="soundNotifications"
                      checked={settings.soundNotifications}
                      onChange={handleSettingChange}
                    />
                  }
                  label="Sound Notifications"
                />

                <FormControlLabel
                  control={
                    <Switch
                      name="emailNotifications"
                      checked={settings.emailNotifications}
                      onChange={handleSettingChange}
                    />
                  }
                  label="Email Notifications"
                />
              </>
            )}
          </Box>
        </Paper>
      </Grid>

      {/* API Settings */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            API Settings
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              fullWidth
              label="API Key"
              type="password"
              value={settings.apiKey}
              disabled
              helperText="Contact administrator to reset your API key"
            />

            <Button variant="outlined">
              Regenerate API Key
            </Button>
          </Box>
        </Paper>
      </Grid>

      {/* About */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            About
          </Typography>
          <Divider sx={{ mb: 2 }} />

          <Box display="flex" flexDirection="column" gap={1}>
            <Box>
              <Typography variant="caption" color="textSecondary">
                Application Version
              </Typography>
              <Typography variant="body2">1.0.0</Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                API Version
              </Typography>
              <Typography variant="body2">1.0.0</Typography>
            </Box>

            <Box>
              <Typography variant="caption" color="textSecondary">
                Last Updated
              </Typography>
              <Typography variant="body2">
                {new Date().toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* Save Button */}
      <Grid item xs={12}>
        <Box display="flex" gap={2}>
          <Button
            variant="contained"
            size="large"
            onClick={handleSave}
          >
            Save Settings
          </Button>

          <Button
            variant="outlined"
            size="large"
            onClick={() => setSettings({
              theme: themeMode,
              autoRefresh: true,
              refreshInterval: 30,
              notifications: true,
              soundNotifications: false,
              emailNotifications: false,
              apiKey: '••••••••••••••••',
              showLogs: true
            })}
          >
            Reset to Defaults
          </Button>
        </Box>
      </Grid>
    </Grid>
  );
};

export default Settings;
