import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Paper,
  TextField,
  Button,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Card,
  CardContent
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useJobs } from '@hooks/useJobs';
import { Priority } from '@types';

const QuickGenerate = () => {
  const navigate = useNavigate();
  const { generateVideo, loading } = useJobs();

  const [formData, setFormData] = useState({
    prompt: '',
    priority: Priority.MEDIUM,
    duration: 30,
    style: 'cinematic'
  });

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleFieldChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'duration' ? parseInt(value) : value
    }));
  };

  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!formData.prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    try {
      const jobId = await generateVideo(formData.prompt, formData.priority);
      setSuccess(true);
      setFormData({
        prompt: '',
        priority: Priority.MEDIUM,
        duration: 30,
        style: 'cinematic'
      });

      // Redirect to job detail
      setTimeout(() => {
        navigate(`/jobs/${jobId}`);
      }, 1000);
    } catch (error: any) {
      setError(error.message || 'Failed to generate video');
    }
  };

  return (
    <Grid container spacing={3} maxWidth="800px" mx="auto">
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Quick Generate
        </Typography>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Create a new video by describing what you want to see
        </Typography>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Grid>
      )}

      {success && (
        <Grid item xs={12}>
          <Alert severity="success">
            Video generation started! Redirecting to job details...
          </Alert>
        </Grid>
      )}

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box component="form" onSubmit={handleSubmit} display="flex" flexDirection="column" gap={3}>
            {/* Prompt */}
            <TextField
              fullWidth
              multiline
              rows={4}
              name="prompt"
              label="Video Prompt"
              placeholder="Describe the video you want to generate... (e.g., 'A sunset over the ocean with waves crashing on the shore')"
              value={formData.prompt}
              onChange={handleFieldChange}
              disabled={loading}
              helperText="Be descriptive for best results"
            />

            {/* Priority */}
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formData.priority}
                onChange={handleSelectChange}
                label="Priority"
                disabled={loading}
              >
                {Object.values(Priority).map((priority: any) => (
                  <MenuItem key={String(priority)} value={priority}>
                    {String(priority).charAt(0).toUpperCase() + String(priority).slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Style */}
            <FormControl fullWidth>
              <InputLabel>Style</InputLabel>
              <Select
                name="style"
                value={formData.style}
                onChange={handleSelectChange}
                label="Style"
                disabled={loading}
              >
                <MenuItem value="cinematic">Cinematic</MenuItem>
                <MenuItem value="documentary">Documentary</MenuItem>
                <MenuItem value="vlog">Vlog</MenuItem>
                <MenuItem value="music">Music Video</MenuItem>
                <MenuItem value="tutorial">Tutorial</MenuItem>
                <MenuItem value="promotional">Promotional</MenuItem>
              </Select>
            </FormControl>

            {/* Duration */}
            <TextField
              fullWidth
              type="number"
              name="duration"
              label="Duration (seconds)"
              value={formData.duration}
              onChange={handleFieldChange}
              disabled={loading}
              inputProps={{ min: 10, max: 300, step: 10 }}
              helperText="Between 10 and 300 seconds"
            />

            {/* Submit Button */}
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
              disabled={loading || !formData.prompt.trim()}
            >
              {loading ? 'Generating...' : 'Generate Video'}
            </Button>
          </Box>
        </Paper>
      </Grid>

      {/* Tips Card */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tips for Best Results
            </Typography>
            <Box component="ul" sx={{ pl: 2, mb: 0 }}>
              <Typography component="li" variant="body2" gutterBottom>
                Be specific and descriptive in your prompt
              </Typography>
              <Typography component="li" variant="body2" gutterBottom>
                Mention the mood, lighting, and atmosphere you want
              </Typography>
              <Typography component="li" variant="body2" gutterBottom>
                Use different priority levels based on urgency
              </Typography>
              <Typography component="li" variant="body2">
                Longer videos may take more time to render
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default QuickGenerate;
