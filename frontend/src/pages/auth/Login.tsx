import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Lock, Mail, Loader2 } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('admin@novaworks.example');
  const [password, setPassword] = useState('Demo123!');
  const { login, isLoading, error } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email, password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 p-4">
      <div className="glass w-full max-w-md p-8 rounded-2xl">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">NovaWorks CRM</h1>
          <p className="text-slate-500 mt-2 text-sm">Sign in to manage projects & tasks</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6 border border-red-100 flex items-center gap-2">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Mail size={18} />
              </div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-[#aa3bff] focus:border-[#aa3bff] outline-none transition-all"
                placeholder="admin@novaworks.example"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Lock size={18} />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-3 py-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-[#aa3bff] focus:border-[#aa3bff] outline-none transition-all"
                placeholder="Demo123!"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 bg-[#aa3bff] hover:bg-[#aa3bff]/90 text-white font-medium py-2.5 rounded-lg flex items-center justify-center transition-all disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="animate-spin" size={20} /> : 'Sign In'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700 text-sm text-slate-500">
          <p className="font-medium text-slate-700 dark:text-slate-300 mb-2">Demo Accounts:</p>
          <ul className="space-y-1">
            <li><span className="font-medium">Admin:</span> admin@</li>
            <li><span className="font-medium">Manager:</span> ayesha@</li>
            <li><span className="font-medium">Agent:</span> ali@</li>
            <li className="pt-1 text-xs opacity-70">Domain: novaworks.example</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
