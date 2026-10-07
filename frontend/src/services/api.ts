import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// For Hackathon MVP, we use these robust mocks so the UI works 100% while backend finishes endpoints.
// Toggle this to false when backend is fully connected.
const USE_MOCKS = true;

const MOCK_PROJECTS = [
  { id: '1', name: 'UrbanCart Redesign', client: 'UrbanCart', manager: 'Ayesha Khan', deadline: '2026-10-20', taskCount: 4, description: 'Redesign of the main ecommerce flow.' },
  { id: '2', name: 'QuickServe API', client: 'QuickServe', manager: 'Bilal Ahmed', deadline: '2026-11-05', taskCount: 5, description: 'Backend API migration.' },
  { id: '3', name: 'NovaWorks Landing Page', client: 'NovaWorks', manager: 'Hina Malik', deadline: '2026-10-15', taskCount: 3, description: 'Marketing site update.' }
];

const MOCK_TASKS = [
  { id: '101', title: 'Design System Update', description: 'Update UI components', projectId: '1', projectName: 'UrbanCart Redesign', assignedTo: 'Ali Raza', deadline: '2026-10-10', estimatedHours: 8 },
  { id: '102', title: 'Checkout Flow', description: 'Implement Stripe', projectId: '1', projectName: 'UrbanCart Redesign', assignedTo: 'Ali Raza', deadline: '2026-10-15', estimatedHours: 12 },
  { id: '103', title: 'API Routes', description: 'Setup endpoints', projectId: '2', projectName: 'QuickServe API', assignedTo: 'Hamza Shah', deadline: '2026-10-25', estimatedHours: 16 }
];

const MOCK_USERS = [
  { id: '1', name: 'Admin User', email: 'admin@novaworks.example', role: 'ADMIN', specialization: 'System' },
  { id: '2', name: 'Ayesha Khan', email: 'ayesha@novaworks.example', role: 'MANAGER', specialization: 'Frontend' },
  { id: '3', name: 'Bilal Ahmed', email: 'bilal@novaworks.example', role: 'MANAGER', specialization: 'Backend' },
  { id: '4', name: 'Ali Raza', email: 'ali@novaworks.example', role: 'AGENT', specialization: 'React' },
  { id: '5', name: 'Hamza Shah', email: 'hamza@novaworks.example', role: 'AGENT', specialization: 'Python' }
];

export const authService = {
  login: async (email: string, pass: string) => {
    if (USE_MOCKS) {
      await new Promise(r => setTimeout(r, 800));
      return { access_token: 'mock_token' }; // Actual user parsing handled in AuthContext for MVP
    }
    const res = await api.post('/api/auth/login', { email, password: pass });
    return res.data;
  }
};

export const transcriptService = {
  process: async (transcript: string) => {
    if (USE_MOCKS) {
      await new Promise(r => setTimeout(r, 2000));
      return { message: 'Processed', projects_created: 3, tasks_created: 12, projects: MOCK_PROJECTS };
    }
    const res = await api.post('/api/transcripts/process', { transcript });
    return res.data;
  }
};

export const projectService = {
  getAll: async () => {
    if (USE_MOCKS) return MOCK_PROJECTS;
    const res = await api.get('/api/projects');
    return res.data;
  },
  getById: async (id: string) => {
    if (USE_MOCKS) {
      const proj = MOCK_PROJECTS.find(p => p.id === id);
      const tasks = MOCK_TASKS.filter(t => t.projectId === id);
      return { ...proj, tasks };
    }
    const res = await api.get(`/api/projects/${id}`);
    return res.data;
  }
};

export const taskService = {
  getMyTasks: async () => {
    if (USE_MOCKS) return MOCK_TASKS;
    const res = await api.get('/api/tasks/my');
    return res.data;
  }
};

export const userService = {
  getAll: async () => {
    if (USE_MOCKS) return MOCK_USERS;
    const res = await api.get('/api/users');
    return res.data;
  }
};
