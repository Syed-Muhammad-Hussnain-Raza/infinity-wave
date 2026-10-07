export type Role = 'ADMIN' | 'MANAGER' | 'AGENT';

export interface User {
  id: number | string;
  name: string;
  email: string;
  role: Role;
  specialization?: string | null;
  skills?: string | null;
}

export interface Task {
  id: number;
  project_id: number;
  project_name?: string | null;
  title: string;
  description?: string | null;
  assignee?: User | null;
  deadline?: string | null;
  estimated_hours?: number | null;
  created_at?: string | null;
}

export interface Project {
  id: number;
  name: string;
  client_name: string;
  description?: string | null;
  manager?: User | null;
  deadline?: string | null;
  task_count: number;
  tasks?: Task[];
  created_at?: string | null;
}

export interface TranscriptProjectSummary {
  id: number;
  name: string;
  client_name: string;
  deadline?: string | null;
  task_count: number;
}

export interface TranscriptProcessResponse {
  message: string;
  ai_provider?: string;
  projects_created: number;
  tasks_created: number;
  projects: TranscriptProjectSummary[];
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
