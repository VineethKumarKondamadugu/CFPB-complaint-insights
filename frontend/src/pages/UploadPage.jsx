import React, { useState } from 'react';
import {
  Box, Typography, Button, LinearProgress, Alert, Paper,
} from '@mui/material';
import { uploadFile } from '../services/api';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setError(''); setResult(null);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await uploadFile(fd);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>Upload Feedback File</Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Supported formats: CSV, XLSX. Required columns: date_received, narrative.
      </Typography>
      <Paper sx={{ p: 3, mt: 2 }}>
        <input type="file" accept=".csv,.xlsx,.xls" onChange={e => setFile(e.target.files[0])} />
        <Box mt={2}>
          <Button variant="contained" onClick={handleUpload} disabled={!file || loading}>
            Upload & Analyze
          </Button>
        </Box>
        {loading && <LinearProgress sx={{ mt: 2 }} />}
        {result && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Ingested {result.ingested} of {result.total} records.
          </Alert>
        )}
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      </Paper>
    </Box>
  );
}
