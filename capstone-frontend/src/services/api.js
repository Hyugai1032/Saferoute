import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add access token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh token on 401
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

const refreshToken = localStorage.getItem('refresh_token');
if (!refreshToken) {
  localStorage.clear();
  window.location.href = '/auth/login';
  return Promise.reject(error);
}

      try {
        const res = await axios.post(
          'http://127.0.0.1:8000/api/auth/refresh/',
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', res.data.access);

        originalRequest.headers.Authorization = `Bearer ${res.data.access}`;

        return api(originalRequest); // Retry with new token
      } catch (err) {
        console.error("Token refresh failed:", err);
        localStorage.clear();
        window.location.href = '/auth/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
