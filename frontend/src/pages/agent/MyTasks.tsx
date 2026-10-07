import { useEffect, useState } from 'react';
import { taskService } from '../../services/api';
import { CheckSquare, Clock, FolderKanban } from 'lucide-react';

export default function MyTasks() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    taskService.getMyTasks().then(data => {
      setTasks(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-12 text-center text-slate-500 animate-pulse font-medium">Loading your tasks...</div>;

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <CheckSquare className="text-[#aa3bff]" /> My Assigned Tasks
      </h1>
      
      {tasks.length === 0 ? (
        <div className="glass p-12 text-center rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-slate-500 font-medium">You have no tasks assigned right now. Great job!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {tasks.map(t => (
            <div key={t.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:border-[#aa3bff]/40 transition-colors">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{t.title}</h3>
                <span className="bg-[#aa3bff]/10 text-[#aa3bff] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                  Due {t.deadline}
                </span>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-5 leading-relaxed">{t.description}</p>
              
              <div className="flex items-center gap-5 text-sm font-medium text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg w-fit border border-slate-100 dark:border-slate-700/50">
                <span className="flex items-center gap-2"><FolderKanban size={16} className="text-[#aa3bff]" /> {t.projectName}</span>
                <div className="w-px h-5 bg-slate-300 dark:bg-slate-600"></div>
                <span className="flex items-center gap-2"><Clock size={16} className="text-slate-400" /> {t.estimatedHours} hours est.</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
