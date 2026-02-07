import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8004',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Don't redirect if it's a login attempt (401 here means wrong password)
        if (error.response && error.response.status === 401 && !error.config.url.includes('/auth/token')) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
