import axios from 'axios';

console.log("API:", import.meta.env.VITE_API_BASE_URL);

const API_URL = import.meta.env.VITE_API_BASE_URL;

export const register = async (userData) => {
  try {
    const response = await axios.post(API_URL + '/auth/register/', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Registration failed' };
  }
};

export const login = async (credentials) => {
  try {
    const payload = {
      email: credentials.email,
      password: credentials.password
    };

    // FIXED URL
    const response = await axios.post(API_URL + 'auth/login/', payload);

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('isAuthenticated', 'true');

    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Login failed' };
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userData');
};

export const getAuthHeader = () => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const getUserProfile = async () => {
  try {
    const response = await axios.get(API_URL + 'user/profile/', {
      headers: getAuthHeader()
    });
    return response.data;
  } catch (error) {
    throw error.response?.data;
  }
};