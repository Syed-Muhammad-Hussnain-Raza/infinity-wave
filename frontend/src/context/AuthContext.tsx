import { createContext, useContext, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

export type Role = 'ADMIN' | 'MANAGER' | 'AGENT';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // Mock API delay to simulate backend auth
      await new Promise(res => setTimeout(res, 800));

      let role: Role = 'AGENT';
      let name = 'Agent';
      if (email.startsWith('admin')) { role = 'ADMIN'; name = 'Admin'; }
      else if (email.startsWith('ayesha') || email.startsWith('bilal') || email.startsWith('hina')) { role = 'MANAGER'; name = 'Manager'; }
      else if (email === 'fail@test.com') throw new Error('Invalid credentials');

      const mockUser = { id: '1', name, email, role };
      setUser(mockUser);
      setToken('mock_token_123'); // Store securely in production

      // Route dynamically based on role
      if (role === 'ADMIN') navigate('/admin');
      else if (role === 'MANAGER') navigate('/manager');
      else navigate('/my-tasks');
    } catch (err: any) {
      setError(err.message || 'Login failed. Try demo credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
