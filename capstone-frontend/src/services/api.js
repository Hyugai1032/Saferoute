import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
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

    // Guest-safe requests (pass { publicOk: true } in the call config, e.g.
    // the public GIS map's overview/route/detail calls) must never get
    // hijacked into a login redirect. A stale/expired token sitting in
    // localStorage shouldn't be able to bounce a visitor who was never
    // required to log in in the first place.
    if (error.response?.status === 401 && originalRequest.publicOk) {
      // First failure: the 401 might just be a stale token. Retry once
      // with no Authorization header at all, exactly like a fresh guest.
      if (!originalRequest._retriedPublic) {
        originalRequest._retriedPublic = true;
        delete originalRequest.headers.Authorization;
        return api(originalRequest);
      }
      // Still failing with no token attached at all means this endpoint
      // genuinely requires login — but this is a public-facing request,
      // so we still must not redirect. Let the caller's own error
      // handling deal with it instead of bouncing the guest to /login.
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

const refreshToken = localStorage.getItem('refresh_token');
if (!refreshToken) {
  localStorage.clear();
  window.location.href = '/auth/login/';
  return Promise.reject(error);
}

      try {
        const res = await api.post(
          "auth/refresh/",
          { refresh: refreshToken }
        );

        localStorage.setItem('access_token', res.data.access);

        originalRequest.headers.Authorization = `Bearer ${res.data.access}`;

        return api(originalRequest); // Retry with new token
      } catch (err) {
        console.error("Token refresh failed:", err);
        localStorage.clear();
        window.location.href = '/auth/login/';
      }
    }

    return Promise.reject(error);
  }
);


export const evacLogsApi = {
  list(params) {
    return api.get("evac_centers/evacuation-logs/", { params });
  },
  create(payload) {
    return api.post("evac_centers/evacuation-logs/", payload);
  },
  latestByCenter(centerId) {
    return api.get("evac_centers/evacuation-logs/latest_by_center/", { params: { center: centerId } });
  },
};

export default api;