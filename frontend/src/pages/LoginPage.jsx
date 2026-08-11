import React, { useState } from 'react';
import { login } from '../services/api';
import { Box, Button, TextField, Typography, Alert, Paper } from '@mui/material';

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await login(email, password);
      localStorage.setItem('access_token', res.data.access_token);
      onLogin();
    } catch {
      setError('Invalid credentials');
    }
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
      <Paper sx={{ p: 4, width: 360 }}>
        <Typography variant="h5" gutterBottom>CFPB Insights — Sign In</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <TextField label="Email" fullWidth margin="normal" value={email}
            onChange={e => setEmail(e.target.value)} type="email" required />
          <TextField label="Password" fullWidth margin="normal" value={password}
            onChange={e => setPassword(e.target.value)} type="password" required />
          <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
            Sign In
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
