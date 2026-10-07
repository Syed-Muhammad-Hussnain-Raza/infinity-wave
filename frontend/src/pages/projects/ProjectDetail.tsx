import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectService } from '../../services/api';
import { ArrowLeft, Clock, User, CheckCircle2 } from 'lucide-react';

export default function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      projectService.getById(id).then(data => {
        setProject(data);
        setLoading(false);
      });
    }
  }, [id]);

  if (loading) return <div className="p-12 text-center text-slate-500 animate-pulse font-medium">Loading project details...</div>;
  if (!project) return <div className="p-12 text-center text-red-500 font-medium">Project not found</div>;

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/projects" className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-[#aa3bff] mb-6 transition-colors">
        <ArrowLeft size={16} /> Back to Projects
      </Link>
      
      <div className="glass p-8 rounded-2xl mb-8 border border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{project.name}</h1>
            <p className="text-lg font-medium text-slate-500">{project.client}</p>
          </div>
          <span className="bg-[#aa3bff]/10 text-[#aa3bff] px-4 py-1.5 rounded-full text-sm font-semibold tracking-wide uppercase">
            Due {project.deadline}
          </span>
        </div>
        <p className="text-slate-700 dark:text-slate-300 mt-6 max-w-3xl leading-relaxed">{project.description}</p>
        <div className="mt-8 inline-flex items-center gap-2 text-sm bg-slate-100 dark:bg-slate-800 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700">
          <User size={16} className="text-slate-500" />
          <span className="text-slate-500 font-medium">Manager:</span> <span className="font-bold text-slate-900 dark:text-white">{project.manager}</span>
        </div>
      </div>

      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <CheckCircle2 className="text-[#aa3bff]" size={20} />
        Assigned Tasks ({project.tasks?.length || 0})
      </h2>
      
      <div className="space-y-4">
        {project.tasks?.map((t: any) => (
          <div key={t.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 flex justify-between items-center shadow-sm hover:border-[#aa3bff]/50 transition-colors">
            <div className="max-w-2xl">
              <h3 className="font-bold text-slate-900 dark:text-white text-lg">{t.title}</h3>
              <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">{t.description}</p>
            </div>
            <div className="flex items-center gap-8 text-sm">
              <div className="flex flex-col items-end">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Assignee</span>
                <span className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5"><User size={14} className="text-[#aa3bff]" /> {t.assignedTo}</span>
              </div>
              <div className="flex flex-col items-end w-24">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Deadline</span>
                <span className="font-semibold text-slate-900 dark:text-white">{t.deadline}</span>
              </div>
              <div className="flex flex-col items-end w-24">
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Est. Hours</span>
                <span className="font-semibold text-slate-900 dark:text-white flex items-center gap-1.5"><Clock size={14} className="text-slate-400" /> {t.estimatedHours}h</span>
              </div>
            </div>
          </div>
        ))}
        {(!project.tasks || project.tasks.length === 0) && (
          <div className="glass p-8 text-center rounded-xl">
            <p className="text-slate-500 font-medium">No tasks assigned yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
