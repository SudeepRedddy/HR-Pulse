import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for attaching auth tokens if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('hrpulse_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle 401 Unauthorized (invalid/expired tokens)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('hrpulse_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
