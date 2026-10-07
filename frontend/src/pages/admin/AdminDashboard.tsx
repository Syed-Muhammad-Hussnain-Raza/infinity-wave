import { Link } from 'react-router-dom';
import { Bot, FolderKanban, Users, CheckSquare, ArrowRight } from 'lucide-react';

export default function AdminDashboard() {
  return (
    <div className="max-w-5xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-slate-500 mt-2 font-medium">System overview and quick shortcuts</p>
        </div>
        <Link to="/admin/transcript" className="bg-[#aa3bff] hover:bg-[#aa3bff]/90 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-[#aa3bff]/20">
          <Bot size={20} />
          Create from Transcript
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-blue-100/80 text-blue-600 flex items-center justify-center mb-5">
            <FolderKanban size={24} />
          </div>
          <div className="text-4xl font-bold text-slate-900 dark:text-white mb-2">3</div>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Projects</div>
        </div>
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-emerald-100/80 text-emerald-600 flex items-center justify-center mb-5">
            <CheckSquare size={24} />
          </div>
          <div className="text-4xl font-bold text-slate-900 dark:text-white mb-2">12</div>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Tasks</div>
        </div>
        <div className="glass p-6 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-[#aa3bff]/10 text-[#aa3bff] flex items-center justify-center mb-5">
            <Users size={24} />
          </div>
          <div className="text-4xl font-bold text-slate-900 dark:text-white mb-2">5</div>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Team Members</div>
        </div>
      </div>

      <div className="glass rounded-2xl p-8 border border-slate-200 dark:border-slate-700 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Quick Navigation</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link to="/projects" className="p-5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 flex items-center justify-between transition-all shadow-sm group">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg group-hover:bg-[#aa3bff]/10 transition-colors">
                <FolderKanban className="text-slate-500 group-hover:text-[#aa3bff] transition-colors" size={20} />
              </div>
              <span className="font-bold text-slate-700 dark:text-slate-200">View All Projects</span>
            </div>
            <ArrowRight size={18} className="text-slate-400 group-hover:text-[#aa3bff] transition-transform group-hover:translate-x-1" />
          </Link>
          <Link to="/team" className="p-5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 flex items-center justify-between transition-all shadow-sm group">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg group-hover:bg-[#aa3bff]/10 transition-colors">
                <Users className="text-slate-500 group-hover:text-[#aa3bff] transition-colors" size={20} />
              </div>
              <span className="font-bold text-slate-700 dark:text-slate-200">Manage Team Directory</span>
            </div>
            <ArrowRight size={18} className="text-slate-400 group-hover:text-[#aa3bff] transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </div>
  );
}
