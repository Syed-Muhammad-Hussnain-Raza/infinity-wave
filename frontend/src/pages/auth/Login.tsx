import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const DEMO = [
  { label: 'Admin', email: 'admin@novaworks.example' },
  { label: 'Manager (Ayesha)', email: 'ayesha@novaworks.example' },
  { label: 'Agent (Ali)', email: 'ali@novaworks.example' },
];

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuth();

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); login(email, password); };
  const fillDemo = (e: string) => { setEmail(e); setPassword('Demo123!'); };

  return (
    <div className="min-h-screen flex">
      {/* Left: Branding */}
      <div className="hidden lg:flex w-[400px] shrink-0 bg-indigo-700 flex-col p-12 justify-between">
        <div>
          <div className="text-white font-bold text-xl mb-12 tracking-tight">NovaWorks CRM</div>
          <h2 className="text-white text-3xl font-semibold leading-tight mb-4">
            AI-powered project management
          </h2>
          <p className="text-indigo-200 text-sm leading-relaxed">
            Paste a meeting transcript — the AI automatically generates structured projects, assigns managers, and creates agent tasks.
          </p>
          <div className="mt-10 space-y-3">
            {['Admin submits meeting transcript', 'AI extracts projects & tasks', 'Managers see their projects', 'Agents see their tasks'].map((s, i) => (
              <div key={i} className="flex items-center gap-3 text-sm text-indigo-100">
                <span className="w-6 h-6 rounded-full bg-indigo-600 border border-indigo-500 text-white text-xs flex items-center justify-center font-semibold shrink-0">{i + 1}</span>
                {s}
              </div>
            ))}
          </div>
        </div>
        <p className="text-indigo-400 text-xs">NovaWorks · Hackathon Demo</p>
      </div>

      {/* Right: Form */}
      <div className="flex-1 flex items-center justify-center bg-white px-8">
        <div className="w-full max-w-[360px]">
          <div className="mb-8">
            <div className="lg:hidden text-indigo-700 font-bold text-lg mb-6">NovaWorks CRM</div>
            <h1 className="text-xl font-semibold text-gray-900">Sign in to your account</h1>
            <p className="text-gray-500 text-sm mt-1">Use your demo credentials below</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2.5 rounded mb-5">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email address</label>
              <input
                type="email" required value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="you@novaworks.example"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder:text-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password" required value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 placeholder:text-gray-400"
              />
            </div>
            <button
              type="submit" disabled={isLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Quick demo login</p>
            <div className="space-y-2">
              {DEMO.map(d => (
                <button key={d.email} onClick={() => fillDemo(d.email)}
                  className="w-full flex items-center justify-between text-sm px-3 py-2 border border-gray-200 rounded hover:border-indigo-400 hover:text-indigo-700 transition-colors text-gray-600 bg-gray-50"
                >
                  <span className="font-medium">{d.label}</span>
                  <span className="text-gray-400 text-xs font-mono">{d.email.split('@')[0]}@…</span>
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-400 mt-2.5 text-center">All passwords: <span className="font-mono font-medium text-gray-600">Demo123!</span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
