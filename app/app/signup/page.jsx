'use client'
import React, { useState } from 'react';
import { TextField, Button, Typography, CircularProgress, Alert } from '@mui/material';

const Signup = () => {
  // Use state to hold an array of form values
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    phone: '',
  });

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Handle input change for form fields
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const response = await fetch('http://localhost:5000/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      setSuccessMessage('Registration successful! Redirecting...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white flex justify-center items-center min-h-screen">
      <div className="bg-gray-50 p-8 rounded shadow-2xl border-xl w-4/12 flex flex-col space-y-6">
        <Typography variant="h4" align="center" color="black" gutterBottom>
          Sign Up your account
        </Typography>
        <form onSubmit={handleSubmit} className="space-y-6 flex flex-col">
          <div>
            <TextField
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              fullWidth
              variant="filled"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <TextField
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              fullWidth
              variant="filled"
              placeholder="Enter your username"
              pattern="[A-Za-z0-9]{4,20}"
              title="4-20 characters (letters and numbers only)"
            />
          </div>

          <div>
            <TextField
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              fullWidth
              variant="filled"
              placeholder="Enter your email"
              autoComplete="email"
            />
          </div>

          <div>
            <TextField
              label="Phone Number"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              fullWidth
              variant="filled"
              placeholder="Enter your phone number"
              pattern="^\+?[1-9]\d{1,14}$"
              title="Please enter a valid phone number"
            />
          </div>

          <div>
            <TextField
              label="Password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              fullWidth
              variant="filled"
              placeholder="Enter your password"
              pattern="(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"
              title="8+ chars with uppercase, lowercase, and numbers"
              autoComplete="new-password"
              type="password"
            />
          </div>

          {/* Error Message */}
          {errorMessage && (
            <Alert severity="error" variant="outlined" sx={{ marginTop: 2 }}>
              {errorMessage}
            </Alert>
          )}

          {/* Success Message */}
          {successMessage && (
            <Alert severity="success" variant="outlined" sx={{ marginTop: 2 }}>
              {successMessage}
            </Alert>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ marginTop: 2 }}
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} color="inherit" />}
          >
            {loading ? 'Signing Up...' : 'Sign Up'}
          </Button>
        </form>

        {/* Link to Login */}
        <Typography variant="body2" align="center" color="black" sx={{ marginTop: 2 }}>
          Already have an account?{' '}
          <a href="/login" className="text-blue-500 hover:text-blue-700">
            Login here
          </a>
        </Typography>
      </div>
    </div>
  );
};

export default Signup;
