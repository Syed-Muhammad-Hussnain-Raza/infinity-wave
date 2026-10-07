import axios from 'axios';
import type {
  User,
  Project,
  Task,
  TranscriptProcessResponse,
  LoginResponse,
} from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({ baseURL: API_URL });

// Automatically inject token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Automatically handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ───────────────────────────────────────────────────────────────────

export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const res = await api.post<LoginResponse>('/api/auth/login', { email, password });
    return res.data;
  },
  me: async (): Promise<User> => {
    const res = await api.get<User>('/api/auth/me');
    return res.data;
  },
};

// ─── Transcripts ─────────────────────────────────────────────────────────────

export const transcriptService = {
  process: async (transcript: string): Promise<TranscriptProcessResponse> => {
    const res = await api.post<TranscriptProcessResponse>('/api/transcripts/process', { transcript });
    return res.data;
  },
};

// ─── Projects ─────────────────────────────────────────────────────────────────

export const projectService = {
  getAll: async (): Promise<Project[]> => {
    const res = await api.get<Project[]>('/api/projects');
    return res.data;
  },
  getById: async (id: string | number): Promise<Project> => {
    const res = await api.get<Project>(`/api/projects/${id}`);
    return res.data;
  },
};

// ─── Tasks ────────────────────────────────────────────────────────────────────

export const taskService = {
  getMyTasks: async (): Promise<Task[]> => {
    const res = await api.get<Task[]>('/api/tasks/my');
    return res.data;
  },
};

// ─── Users ────────────────────────────────────────────────────────────────────

export const userService = {
  getAll: async (): Promise<User[]> => {
    const res = await api.get<User[]>('/api/users');
    return res.data;
  },
};
