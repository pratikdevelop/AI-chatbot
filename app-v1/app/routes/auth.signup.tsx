'use client';
import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { Button, TextField } from '@mui/material';
import { Link, useNavigate, useNavigation } from '@remix-run/react';
import axios from 'axios';

const Signup = () => {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    phone: '',
  });
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError('');
    setLoading(true);

    try {
      // Create user with email and password
        const userCredential = await axios.post('http://localhost:3001/api/auth/signup', {
            email: form.email,
            password: form.password,
                    name: form.name,
                    phone: form.phone,
      }
      );
     
        console.log('User signed up and data saved successfully!');
        
    } catch (error: any) {
      console.error('Error in signup:', error);
      setError(error.message || 'Failed to sign up. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex relative h-[100vh] w-full items-center justify-center">
      <Box className="flex flex-col w-[34vw] bg-white border-2 shadow-2xl p-8 space-y-6" component="form">
        <span  className='text-3xl font-bold'>
          Create Your Account
        </span>

        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}

        <TextField
          id="name"
          name="name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          label="Full Name"
          fullWidth
        />
        <TextField
          id="email"
          name="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          label="Email"
          fullWidth
        />
        <TextField
          id="phone"
          name="phone"
          value={form.phone}
          onChange={(e) => setForm({ ...form, phone: e.target.value })}
          label="Phone Number"
          fullWidth
        />
        <TextField
          id="password"
          name="password"
          type="password"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          label="Password"
          fullWidth
        />
        <span className='text-slate-900 text-sm ml-auto'>
          Already have an account?
          <Link to='/auth/login' className='text-blue-800'>
            Login now
          </Link>

        </span>

        <Button
          variant="contained"
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          fullWidth
        >
          {loading ? 'Signing Up...' : 'Signup'}
        </Button>
      </Box>
    </div>
  );
};

export default Signup;