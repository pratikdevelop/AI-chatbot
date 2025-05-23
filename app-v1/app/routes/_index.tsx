'use client';
import * as React from 'react';
import {
  Box,
  Drawer,
  Toolbar,
  List,
  Typography,
  Divider,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  Button,
  AppBar,
  CssBaseline,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Skeleton,
  Collapse,
  IconButton,
  Autocomplete,
} from '@mui/material';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import axios from 'axios';
import { useDebouncedCallback } from 'use-debounce';

const drawerWidth = 240;
const API_BASE_URL = 'http://localhost:3001';

// Type definitions
interface User {
  id: string;
  email: string;
  user_metadata?: {
    name?: string;
    phone?: string;
  };
}

interface ImagePair {
  pair_id?: string;
  image_1: string;
  image_2: string;
  prompt?: string;
}

interface ImageData {
  prompt: string;
  generatedImage: string;
  originalPair: ImagePair;
}

interface PreferenceStats {
  [key: string]: number;
}

interface LogEntry {
  type: 'error' | 'success';
  message: string;
  timestamp: string;
}

export default function PersistentDrawerRight() {
  const [view, setView] = React.useState<'generate' | 'signup' | 'signin' | 'profile' | 'imagePair' | 'generateImage' | 'preferences'>('generate');
  const [name, setName] = React.useState<string>('');
  const [email, setEmail] = React.useState<string>('');
  const [password, setPassword] = React.useState<string>('');
  const [fullName, setFullName] = React.useState<string>('');
  const [phone, setPhone] = React.useState<string>('');
  const [generatedText, setGeneratedText] = React.useState<string>('');
  const [imageData, setImageData] = React.useState<ImageData | null>(null);
  const [imagePair, setImagePair] = React.useState<ImagePair | null>(null);
  const [preferenceStats, setPreferenceStats] = React.useState<PreferenceStats | null>(null);
  const [user, setUser] = React.useState<User | null>(null);
  const [error, setError] = React.useState<string>('');
  const [logEntries, setLogEntries] = React.useState<LogEntry[]>([]);
  const [loading, setLoading] = React.useState<boolean>(false);
  const [customPrompt, setCustomPrompt] = React.useState<string>('');
  const [recentPrompts, setRecentPrompts] = React.useState<string[]>([]);
  const [showLog, setShowLog] = React.useState<boolean>(false);
  const [token, setToken] = React.useState<string | null>(typeof window !== 'undefined' ? localStorage.getItem('token') : null);

  // Load recent prompts from localStorage
  React.useEffect(() => {
    const saved = localStorage.getItem('recentPrompts');
    if (saved) {
      const prompts = JSON.parse(saved);
      setRecentPrompts(prompts);
      setCustomPrompt(prompts[0] || '');
    }
  }, []);

  // Save custom prompt to localStorage
  React.useEffect(() => {
    if (customPrompt) {
      const updated = [customPrompt, ...recentPrompts.filter((p) => p !== customPrompt)].slice(0, 5);
      setRecentPrompts(updated);
      localStorage.setItem('recentPrompts', JSON.stringify(updated));
    }
  }, [customPrompt]);

  // Set axios default headers
  React.useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      getProfile();
    }
  }, [token]);

  // Fetch data when view changes
  React.useEffect(() => {
    if (view === 'imagePair') {
      handleGetImagePair();
    } else if (view === 'generateImage') {
      debouncedGenerateImage();
    } else if (view === 'preferences') {
      handleGetPreferenceStats();
    }
  }, [view]);

  // Log messages to logEntries
  const logMessage = (type: 'error' | 'success', message: string) => {
    setLogEntries((prev) => [
      ...prev,
      { type, message, timestamp: new Date().toLocaleString() },
    ].slice(-10));
    if (type === 'error') {
      setError(message);
    }
  };

  // Debounced generate image function
  const debouncedGenerateImage = useDebouncedCallback(async (retryCount = 0, maxRetries = 3) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/generate-image${customPrompt ? `?prompt=${encodeURIComponent(customPrompt)}` : ''}`
      );
      setImageData(response.data);
      logMessage('success', `Image generated with prompt: ${response.data.prompt}`);
      setError('');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to generate image';
      console.error('Generate image error:', err);
      let retry = false;
      if (
        (errorMessage.includes('Prompt not found') ||
          errorMessage.includes('rate limit') ||
          errorMessage.includes('authentication') ||
          errorMessage.includes('404')) &&
        retryCount < maxRetries
      ) {
        console.log(`Retrying image generation (attempt ${retryCount + 1}/${maxRetries})`);
        retry = true;
      }
      logMessage('error', errorMessage);
      if (retry) {
        return debouncedGenerateImage(retryCount + 1, maxRetries);
      } else if (retryCount >= maxRetries) {
        setImageData({
          prompt: 'Fallback image',
          generatedImage: '/fallback.jpg',
          originalPair: {},
        });
        logMessage('error', 'Max retries reached, using fallback image');
      }
    } finally {
      setLoading(false);
    }
  }, 500);

  // Fetch user profile
  const getProfile = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/profile`);
      setUser(response.data.user);
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  };

  // Handle /generate
  const handleGenerate = async () => {
    if (!name.trim()) {
      logMessage('error', 'Please enter a question');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/generate?search=${encodeURIComponent(name)}`);
      setGeneratedText(response.data.message);
      logMessage('success', 'Text generated successfully');
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Failed to generate text');
    } finally {
      setLoading(false);
    }
  };

  // Handle /api/auth/signup
  const handleSignup = async () => {
    if (!email || !password || !fullName) {
      logMessage('error', 'Email, password, and name are required');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, {
        email,
        password,
        name: fullName,
        phone,
      });
      setToken(response.data.token.access_token);
      localStorage.setItem('token', response.data.token.access_token);
      setUser(response.data.user);
      setView('profile');
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  // Handle /api/auth/signin
  const handleSignin = async () => {
    if (!email || !password) {
      logMessage('error', 'Email and password are required');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/signin`, {
        email,
        password,
      });
      setToken(response.data.token.access_token);
      localStorage.setItem('token', response.data.token.access_token);
      setUser(response.data.user);
      setView('profile');
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Signin failed');
    } finally {
      setLoading(false);
    }
  };

  // Handle /api/image-pair
  const handleGetImagePair = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/image-pair`);
      setImagePair(response.data.pair);
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Failed to fetch image pair');
    } finally {
      setLoading(false);
    }
  };

  // Handle /api/submit-preference
  const handleSubmitPreference = async (pairId: string, preference: string) => {
    if (!user) {
      logMessage('error', 'Please sign in to submit preferences');
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/submit-preference`, {
        pairId,
        preference,
        userId: user.id,
      });
      setError('');
      handleGetPreferenceStats();
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Failed to submit preference');
    } finally {
      setLoading(false);
    }
  };

  // Handle /api/preference-stats
  const handleGetPreferenceStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/preference-stats`);
      setPreferenceStats(response.data.stats);
      setError('');
    } catch (err: any) {
      logMessage('error', err.response?.data?.message || 'Failed to fetch preference stats');
    } finally {
      setLoading(false);
    }
  };

  // Handle logout
  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setView('signin');
    setImageData(null);
    setImagePair(null);
    setPreferenceStats(null);
    setGeneratedText('');
    setError('');
    setLogEntries([]);
    setCustomPrompt('');
  };

  // Drawer menu items
  const menuItems = [
    { text: 'Ask a Question', view: 'generate', icon: <InboxIcon /> },
    { text: 'Sign Up', view: 'signup', icon: <MailIcon />, hidden: !!user },
    { text: 'Sign In', view: 'signin', icon: <InboxIcon />, hidden: !!user },
    { text: 'Profile', view: 'profile', icon: <MailIcon />, hidden: !user },
    { text: 'Image Pair', view: 'imagePair', icon: <InboxIcon /> },
    { text: 'Generate Image', view: 'generateImage', icon: <MailIcon /> },
    { text: 'Preferences', view: 'preferences', icon: <InboxIcon /> },
    { text: 'Logout', view: 'logout', icon: <MailIcon />, hidden: !user },
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            AI Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar />
        <Divider />
        <List>
          {menuItems.map((item) => (
            !item.hidden && (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  onClick={() => {
                    if (item.view === 'logout') {
                      handleLogout();
                    } else {
                      setView(item.view);
                      setError('');
                    }
                  }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            )
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error.includes('404')
              ? 'Image generation model unavailable. Please try again later or use a different prompt.'
              : error.includes('rate limit')
              ? 'Hugging Face API rate limit exceeded. Please try again later or use a custom prompt.'
              : error.includes('authentication')
              ? 'Hugging Face API authentication failed. Please check your API key.'
              : error.includes('Prompt not found')
              ? 'No valid prompt found. Using fallback image.'
              : error}
            {(error.includes('Failed to generate image') ||
              error.includes('Prompt not found') ||
              error.includes('rate limit') ||
              error.includes('404') ||
              error.includes('authentication')) && (
              <Button
                size="small"
                onClick={() => debouncedGenerateImage()}
                sx={{ ml: 2 }}
                aria-label="Retry image generation"
              >
                Retry
              </Button>
            )}
          </Alert>
        )}
        <Box sx={{ mb: 2 }}>
          <Button
            variant="text"
            onClick={() => setShowLog(!showLog)}
            endIcon={showLog ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            aria-label={showLog ? 'Hide log' : 'Show log'}
          >
            {showLog ? 'Hide Log' : 'Show Log'}
          </Button>
          <Collapse in={showLog}>
            <Box sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'grey.100', p: 1 }}>
              {logEntries.length > 0 ? (
                logEntries.map((log, index) => (
                  <Typography
                    key={index}
                    variant="caption"
                    display="block"
                    color={log.type === 'error' ? 'error.main' : 'success.main'}
                  >
                    [{log.timestamp}] {log.message}
                  </Typography>
                ))
              ) : (
                <Typography variant="caption">No logs available</Typography>
              )}
            </Box>
          </Collapse>
        </Box>
        {loading && <CircularProgress sx={{ display: 'block', mx: 'auto', my: 2 }} />}

        {/* Generate View */}
        {view === 'generate' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Ask a Question</Typography>
            <TextField
              variant="outlined"
              label="Enter your question"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Question input"
            />
            <Button
              variant="contained"
              onClick={handleGenerate}
              disabled={loading || !name.trim()}
              sx={{ mt: 2 }}
              aria-label="Generate text"
            >
              Generate
            </Button>
            {generatedText && (
              <Typography variant="body1" sx={{ mt: 2 }}>
                <strong>Response:</strong> {generatedText}
              </Typography>
            )}
          </Box>
        )}

        {/* Signup View */}
        {view === 'signup' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Sign Up</Typography>
            <TextField
              variant="outlined"
              label="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Email input"
            />
            <TextField
              variant="outlined"
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Password input"
            />
            <TextField
              variant="outlined"
              label="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Full name input"
            />
            <TextField
              variant="outlined"
              label="Phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Phone input"
            />
            <Button
              variant="contained"
              onClick={handleSignup}
              disabled={loading || !email || !password || !fullName}
              sx={{ mt: 2 }}
              aria-label="Sign up"
            >
              Sign Up
            </Button>
          </Box>
        )}

        {/* Signin View */}
        {view === 'signin' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Sign In</Typography>
            <TextField
              variant="outlined"
              label="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Email input"
            />
            <TextField
              variant="outlined"
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              fullWidth
              margin="normal"
              aria-label="Password input"
            />
            <Button
              variant="contained"
              onClick={handleSignin}
              disabled={loading || !email || !password}
              sx={{ mt: 2 }}
              aria-label="Sign in"
            >
              Sign In
            </Button>
          </Box>
        )}

        {/* Profile View */}
        {view === 'profile' && user && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>User Profile</Typography>
            <Typography><strong>Email:</strong> {user.email}</Typography>
            <Typography><strong>Name:</strong> {user.user_metadata?.name || 'N/A'}</Typography>
            <Typography><strong>Phone:</strong> {user.user_metadata?.phone || 'N/A'}</Typography>
            <Button
              variant="outlined"
              color="error"
              onClick={handleLogout}
              sx={{ mt: 2 }}
              aria-label="Logout"
            >
              Logout
            </Button>
          </Box>
        )}

        {/* Image Pair View */}
        {view === 'imagePair' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Image Pair</Typography>
            {imagePair ? (
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Card>
                    <CardMedia
                      component="img"
                      height="200"
                      image={imagePair.image_1 || '/placeholder.jpg'}
                      alt="Image 1"
                    />
                    <CardContent>
                      <Button
                        variant="contained"
                        onClick={() => handleSubmitPreference(imagePair.pair_id || 'default', 'image_1')}
                        disabled={loading || !user}
                        aria-label="Prefer image 1"
                      >
                        Prefer Image 1
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6}>
                  <Card>
                    <CardMedia
                      component="img"
                      height="200"
                      image={imagePair.image_2 || '/placeholder.jpg'}
                      alt="Image 2"
                    />
                    <CardContent>
                      <Button
                        variant="contained"
                        onClick={() => handleSubmitPreference(imagePair.pair_id || 'default', 'image_2')}
                        disabled={loading || !user}
                        aria-label="Prefer image 2"
                      >
                        Prefer Image 2
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            ) : (
              <Box>
                <Skeleton variant="rectangular" width="100%" height={200} animation="wave" />
                <Typography sx={{ mt: 2 }}>
                  No image pair available. {error ? 'Please try again.' : 'Loading...'}
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {/* Generate Image View */}
        {view === 'generateImage' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Generated Image</Typography>
            <Autocomplete
              freeSolo
              options={recentPrompts}
              value={customPrompt}
              onChange={(event, newValue) => setCustomPrompt(newValue || '')}
              renderInput={(params) => (
                <TextField
                  {...params}
                  variant="outlined"
                  label="Enter custom prompt (optional)"
                  placeholder="E.g., A futuristic city at night"
                  margin="normal"
                  fullWidth
                  aria-label="Custom prompt input"
                  onChange={(e) => setCustomPrompt(e.target.value)}
                />
              )}
            />
            {imageData ? (
              <Card>
                <CardMedia
                  component="img"
                  height="300"
                  image={imageData.generatedImage || '/placeholder.jpg'}
                  alt="Generated Image"
                  sx={{ objectFit: 'contain', transition: 'opacity 0.3s' }}
                />
                <CardContent>
                  <Typography><strong>Prompt:</strong> {imageData.prompt}</Typography>
                </CardContent>
              </Card>
            ) : (
              <Box>
                <Skeleton variant="rectangular" width="100%" height={300} animation="wave" />
                <Typography sx={{ mt: 2 }}>
                  No image generated. {error ? 'Click "Generate New Image" to try again.' : 'Loading...'}
                </Typography>
              </Box>
            )}
            <Button
              variant="contained"
              onClick={() => debouncedGenerateImage()}
              disabled={loading}
              sx={{ mt: 2 }}
              aria-label="Generate new image"
            >
              {loading ? 'Generating...' : 'Generate New Image'}
            </Button>
          </Box>
        )}

        {/* Preferences View */}
        {view === 'preferences' && (
          <Box>
            <Typography variant="h5" sx={{ mb: 2 }}>Preference Stats</Typography>
            {preferenceStats ? (
              Object.entries(preferenceStats).map(([key, value]) => (
                <Typography key={key}>
                  <strong>{key}:</strong> {value} votes
                </Typography>
              ))
            ) : (
              <Box>
                <Skeleton variant="text" width="50%" animation="wave" />
                <Typography sx={{ mt: 2 }}>
                  No stats available. {error ? 'Please try again.' : 'Loading...'}
                </Typography>
              </Box>
            )}
            <Button
              variant="contained"
              onClick={handleGetPreferenceStats}
              disabled={loading}
              sx={{ mt: 2 }}
              aria-label="Refresh stats"
            >
              Refresh Stats
            </Button>
          </Box>
        )}
      </Box>
    </Box>
  );
}