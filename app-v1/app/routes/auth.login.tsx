'use client';
import { Box, Typography, TextField, Button } from '@mui/material'
import { Link, useNavigate } from '@remix-run/react'
import axios from 'axios';
import React, { useState } from 'react'

const login = () => {
    const [form, setForm] = useState({
      email: '',
      password: '',
    });
    const navigate = useNavigate();
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
  
    const handleSubmit = async () => {
      setError('');
      setLoading(true);
  
      try {
        // Create user with email and password
        const userCredential = await axios.post('http://localhost:3001/api/auth/signin', {
          email: form.email,
          password: form.password,
        });
        localStorage.setItem('User', JSON.stringify(userCredential.data.user))
        localStorage.setItem('session', JSON.stringify(userCredential.data.session))
       
        console.log('User signed up and data saved successfully!');
        navigate('/')
          
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
      <span  className='text-3xl font-bold text-slate-900'>
          Login with your account
      </span>

      <TextField
        id="email"
        name="email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        label="Email"
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
      <span className='text-slate-900 text-sm  text-center'>
        Need to create account? 
        <Link to='/auth/signup' className='text-blue-800'>
          &nbsp;Create account 
        </Link>

      </span>

      <Button
        variant="contained"
        type="button"
        onClick={handleSubmit}
        disabled={loading}
        fullWidth
      >
        {loading ? 'Signing Up...' : 'Sign In'}
        </Button>

    </Box>
  </div>
  )
}

export default login