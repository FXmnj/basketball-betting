import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refreshToken') : null;
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, { refreshToken });
          const { accessToken } = response.data;
          
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', accessToken);
          }
          
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return apiClient(originalRequest);
        }
      } catch (err) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/auth/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Auth
  auth: {
    register: (data: { email: string; password: string; firstName?: string; lastName?: string }) =>
      apiClient.post('/auth/register', data),
    login: (data: { email: string; password: string }) => apiClient.post('/auth/login', data),
    profile: () => apiClient.get('/auth/profile'),
    updateProfile: (data: { firstName?: string; lastName?: string }) =>
      apiClient.patch('/auth/profile', data),
    logout: () => apiClient.post('/auth/logout'),
  },

  // Teams
  teams: {
    getAll: () => apiClient.get('/teams'),
    getById: (id: number) => apiClient.get(`/teams/${id}`),
    getStandings: () => apiClient.get('/teams/standings/current'),
    getStats: (id: number) => apiClient.get(`/teams/${id}/stats`),
  },

  // Players
  players: {
    getAll: () => apiClient.get('/players'),
    getById: (id: number) => apiClient.get(`/players/${id}`),
    getByTeam: (teamId: number) => apiClient.get(`/players?teamId=${teamId}`),
  },

  // Games
  games: {
    getAll: () => apiClient.get('/games'),
    getById: (id: number) => apiClient.get(`/games/${id}`),
    getUpcoming: () => apiClient.get('/games?status=Scheduled'),
    getLive: () => apiClient.get('/games?status=InProgress'),
  },

  // Predictions
  predictions: {
    create: (data: any) => apiClient.post('/predictions', data),
    getByGame: (gameId: number) => apiClient.get(`/predictions?gameId=${gameId}`),
    getUserPredictions: () => apiClient.get('/predictions/user'),
  },
};

export default apiClient;
