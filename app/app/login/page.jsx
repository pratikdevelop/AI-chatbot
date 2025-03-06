'use client';
import React, { useState } from 'react';
import { TextField, Button, Typography, Alert } from '@mui/material';
import axios from 'axios';
import { useRouter } from 'next/navigation'



const Login = () => {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    const formData = {
      username: e.target.username.value,
      password: e.target.password.value,
    };

    try {
      // Use axios to send the form data to Flask backend
      const response = await axios.post('http://localhost:5000api/login', formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Check if the response was successful (you can add additional checks based on response)
        if (response.status === 200) {
            localStorage.setItem('token', response.data.access_token)
            router.push('/')
        // Handle successful login (redirect, display a message, etc.)
        // window.location.href = '/'; // Redirect to the home page or any other page
      }
    } catch (error) {
      // Handle error in case of failed request
      if (error.response) {
        // Handle known errors from the Flask server
        setErrorMessage(error.response.data.error || 'Login failed');
      } else {
        // Handle other errors (network issues, etc.)
        setErrorMessage('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded shadow-lg w-3/12 mx-auto">
      <Typography variant="h4" align="center" gutterBottom>
        Login with your account
      </Typography>
      <form method="POST" onSubmit={handleSubmit}>
        <div className="mb-4">
          <TextField
            label="Username"
            name="username"
            id="username"
            required
            fullWidth
            variant="outlined"
            placeholder="Enter your username"
            margin="normal"
          />
        </div>

        <div className="mb-4">
          <TextField
            label="Password"
            name="password"
            id="password"
            required
            fullWidth
            variant="outlined"
            type="password"
            placeholder="Enter your password"
            margin="normal"
          />
        </div>

        {errorMessage && (
          <Alert severity="error" variant="outlined" sx={{ marginBottom: 2 }}>
            {errorMessage}
          </Alert>
        )}

        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ marginTop: 2 }}
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>

      <Typography variant="body2" align="center" sx={{ marginTop: 2 }}>
        Don't have an account?{' '}
        <a href="/signup" className="text-blue-500">
          Sign up here
        </a>
      </Typography>
    </div>
  );
};

export default Login;
