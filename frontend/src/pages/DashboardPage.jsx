import React, { useEffect, useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, CircularProgress, Alert,
  Table, TableHead, TableRow, TableCell, TableBody, Chip,
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
  getWoW, getMoM, getCategories, getKeywords, getSentiment, getLowConfidence,
  triggerCfpbIngest, downloadPdf, downloadCsv,
} from '../services/api';

const SENTIMENT_COLORS = { Positive: '#4caf50', Neutral: '#ff9800', Negative: '#f44336' };

function MetricCard({ title, value, delta, pct }) {
  const color = delta > 0 ? 'error' : delta < 0 ? 'success' : 'inherit';
  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary">{title}</Typography>
        <Typography variant="h4">{value ?? '—'}</Typography>
        {delta !== undefined && (
          <Typography variant="body2" color={color}>
            {delta > 0 ? '+' : ''}{delta} ({pct}%)
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [wow, setWow] = useState(null);
  const [mom, setMom] = useState(null);
  const [categories, setCategories] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [lowConf, setLowConf] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getWoW(), getMoM(), getCategories(), getKeywords(), getSentiment(), getLowConfidence(),
    ])
      .then(([w, m, c, k, s, lc]) => {
        setWow(w.data); setMom(m.data);
        setCategories(c.data.slice(0, 10));
        setKeywords(k.data.slice(0, 15));
        setSentiment(s.data);
        setLowConf(lc.data.slice(0, 10));
      })
      .catch(() => setError('Failed to load analytics data'))
      .finally(() => setLoading(false));
  }, []);

  const handleIngest = async () => {
    await triggerCfpbIngest();
    alert('CFPB ingestion started');
  };

  const handleDownloadPdf = async () => {
    const res = await downloadPdf({});
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    const a = document.createElement('a'); a.href = url; a.download = 'cfpb_report.pdf'; a.click();
  };

  const handleDownloadCsv = async () => {
    const res = await downloadCsv({});
    const url = URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
    const a = document.createElement('a'); a.href = url; a.download = 'cfpb_complaints.csv'; a.click();
  };

  if (loading) return <Box display="flex" justifyContent="center" mt={8}><CircularProgress /></Box>;

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">CFPB Complaint Insights</Typography>
        <Box display="flex" gap={1}>
          <Button variant="outlined" onClick={handleIngest}>Refresh CFPB Data</Button>
          <Button variant="contained" onClick={handleDownloadPdf}>Export PDF</Button>
          <Button variant="contained" color="secondary" onClick={handleDownloadCsv}>Export CSV</Button>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Trend KPIs */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Complaints (This Week)"
            value={wow?.complaint_count?.current}
            delta={wow?.complaint_count?.delta}
            pct={wow?.complaint_count?.pct_change}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="Complaints (This Month)"
            value={mom?.complaint_count?.current}
            delta={mom?.complaint_count?.delta}
            pct={mom?.complaint_count?.pct_change}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="WoW Change"
            value={`${wow?.complaint_count?.pct_change ?? 0}%`}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <MetricCard
            title="MoM Change"
            value={`${mom?.complaint_count?.pct_change ?? 0}%`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Category bar chart */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Top Categories</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categories} layout="vertical" margin={{ left: 160 }}>
                  <XAxis type="number" />
                  <YAxis dataKey="category" type="category" width={160} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Sentiment pie */}
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Sentiment Distribution</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={sentiment} dataKey="count" nameKey="sentiment" cx="50%" cy="50%" outerRadius={100} label>
                    {sentiment.map((s, i) => (
                      <Cell key={i} fill={SENTIMENT_COLORS[s.sentiment] || '#9e9e9e'} />
                    ))}
                  </Pie>
                  <Legend />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Keywords */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Top Keywords</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {keywords.map((k) => (
                  <Chip key={k.keyword} label={`${k.keyword} (${k.count})`} size="small" />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Low confidence queue */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Low-Confidence Predictions</Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {lowConf.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.id}</TableCell>
                      <TableCell>{c.date_received}</TableCell>
                      <TableCell>{c.taxonomy_category || '—'}</TableCell>
                      <TableCell>{c.taxonomy_confidence != null ? `${(c.taxonomy_confidence * 100).toFixed(0)}%` : '—'}</TableCell>
                    </TableRow>
                  ))}
                  {lowConf.length === 0 && (
                    <TableRow><TableCell colSpan={4}>No low-confidence items</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
