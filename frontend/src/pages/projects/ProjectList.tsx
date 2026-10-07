import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectService } from '../../services/api';
import { FolderKanban, Calendar, Users, ListTodo } from 'lucide-react';

export default function ProjectList({ title = 'Projects' }: { title?: string }) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectService.getAll().then(data => {
      setProjects(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-12 text-center text-slate-500 animate-pulse font-medium">Loading projects...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <FolderKanban className="text-[#aa3bff]" /> {title}
      </h1>
      
      {projects.length === 0 ? (
        <div className="glass p-12 text-center rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-slate-500">No projects found. An admin needs to create them from a transcript.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(p => (
            <Link key={p.id} to={`/projects/${p.id}`} className="glass p-6 rounded-xl hover:-translate-y-1 hover:shadow-md transition-all cursor-pointer block border border-slate-200 dark:border-slate-700">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1 truncate">{p.name}</h2>
              <p className="text-sm font-medium text-slate-500 mb-5">{p.client}</p>
              
              <div className="space-y-2.5 text-sm font-medium text-slate-600 dark:text-slate-400">
                <div className="flex items-center gap-2.5"><Users size={16} className="text-slate-400" /> <span className="text-slate-900 dark:text-white">{p.manager}</span></div>
                <div className="flex items-center gap-2.5"><Calendar size={16} className="text-slate-400" /> <span className="text-slate-900 dark:text-white">{p.deadline}</span></div>
                <div className="flex items-center gap-2.5 mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <ListTodo size={16} className="text-[#aa3bff]" /> 
                  <span className="text-[#aa3bff] font-semibold">{p.taskCount} Active Tasks</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
