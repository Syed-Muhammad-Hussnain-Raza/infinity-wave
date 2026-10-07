import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({ baseURL: API_URL });

// Automatically inject token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ─── Auth ───────────────────────────────────────────────────────────────────

export const authService = {
  login: async (email: string, password: string) => {
    const res = await api.post('/api/auth/login', { email, password });
    return res.data; // { access_token, token_type, user: { id, name, email, role } }
  },
  me: async () => {
    const res = await api.get('/api/auth/me');
    return res.data;
  }
};

// ─── Transcripts ─────────────────────────────────────────────────────────────

export const transcriptService = {
  process: async (transcript: string) => {
    const res = await api.post('/api/transcripts/process', { transcript });
    return res.data; // { message, projects_created, tasks_created, projects: [...] }
  }
};

// ─── Projects ─────────────────────────────────────────────────────────────────

export const projectService = {
  getAll: async () => {
    const res = await api.get('/api/projects');
    return res.data; // Array of { id, name, client, manager, deadline, task_count, description }
  },
  getById: async (id: string) => {
    const res = await api.get(`/api/projects/${id}`);
    return res.data; // { id, name, client, manager, deadline, description, tasks: [...] }
  }
};

// ─── Tasks ────────────────────────────────────────────────────────────────────

export const taskService = {
  getMyTasks: async () => {
    const res = await api.get('/api/tasks/my');
    return res.data; // Array of { id, title, description, project_name, deadline, estimated_hours }
  }
};

// ─── Users ────────────────────────────────────────────────────────────────────

export const userService = {
  getAll: async () => {
    const res = await api.get('/api/users');
    return res.data; // Array of { id, name, email, role, specialization }
  }
};
