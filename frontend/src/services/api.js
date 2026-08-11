import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `******;
  }
  return config;
});

export const login = (email, password) =>
  api.post('/auth/token', new URLSearchParams({ username: email, password }));

export const register = (email, password, full_name) =>
  api.post('/auth/register', { email, password, full_name });

export const getComplaints = (params) => api.get('/complaints/', { params });

export const getComplaint = (id) => api.get(`/complaints/${id}`);

export const triggerCfpbIngest = () => api.post('/ingest/cfpb');

export const uploadFile = (formData) =>
  api.post('/ingest/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });

export const getWoW = () => api.get('/analytics/wow');

export const getMoM = () => api.get('/analytics/mom');

export const getCategories = (params) => api.get('/analytics/categories', { params });

export const getKeywords = (params) => api.get('/analytics/keywords', { params });

export const getSentiment = (params) => api.get('/analytics/sentiment', { params });

export const getLowConfidence = (params) => api.get('/analytics/low-confidence', { params });

export const downloadPdf = (params) =>
  api.get('/reports/pdf', { params, responseType: 'blob' });

export const downloadCsv = (params) =>
  api.get('/reports/csv', { params, responseType: 'blob' });

export default api;
