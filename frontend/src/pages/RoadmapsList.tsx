import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { Map, Terminal, Code, Database, Sparkles, ArrowRight, Search, PlusCircle, Bookmark } from 'lucide-react';

interface Enrollment {
  id: string;
  course_id: string;
  course: {
    id: string;
    title: string;
  } | null;
  progress_percent: number;
}

export default function RoadmapsList() {
  const navigate = useNavigate();
  const [topicInput, setTopicInput] = useState('');

  // Fetch active user enrollments to show enrolled roadmaps
  const { data: enrollmentList } = useQuery<{ items: Enrollment[] }>({
    queryKey: ['userEnrollments'],
    queryFn: async () => {
      const res = await apiClient.get('/enrollments');
      return res.data;
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topicInput.trim()) {
      navigate(`/roadmap/${encodeURIComponent(topicInput.trim().toLowerCase())}`);
    }
  };

  const popularTopics = [
    { name: 'Python', desc: 'Syntax, data structures, and foundational programming.', icon: <Terminal className="w-5 h-5 text-indigo-400" /> },
    { name: 'React', desc: 'Hooks, components, routing, and single-page architectures.', icon: <Code className="w-5 h-5 text-purple-400" /> },
    { name: 'FastAPI', desc: 'Asynchronous API building, schemas, and authentication.', icon: <Sparkles className="w-5 h-5 text-cyan-400" /> },
    { name: 'Machine Learning', desc: 'Neural networks, regression, data models, and pandas.', icon: <Database className="w-5 h-5 text-emerald-400" /> }
  ];

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Learning Roadmaps <Map className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Browse visual path guides or enter a custom topic to auto-import a customized learning roadmap structure.
        </p>
      </div>

      {/* Custom Roadmap Search Input */}
      <form onSubmit={handleSubmit} className="w-full max-w-xl">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 rounded-xl blur opacity-25 group-hover:opacity-35 transition duration-1000 group-focus-within:opacity-40" />
          <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-xl">
            <Search className="w-5 h-5 text-slate-500 ml-4 pointer-events-none" />
            <input
              type="text"
              placeholder="Enter custom topic (e.g. Django, Kubernetes)..."
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              className="w-full bg-transparent px-4 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none text-sm"
            />
            <button
              type="submit"
              className="mr-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs px-4 py-2 rounded-lg transition-all shadow-md flex items-center gap-1.5"
            >
              Generate
            </button>
          </div>
        </div>
      </form>

      {/* Enrolled Active Roadmaps */}
      {enrollmentList?.items && enrollmentList.items.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-indigo-400" /> Enrolled Roadmaps
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {enrollmentList.items.map((e) => (
              <div
                key={e.id}
                onClick={() => navigate(`/roadmap/${e.course?.title.toLowerCase()}`)}
                className="glass-card p-5 hover:border-indigo-500/30 cursor-pointer flex flex-col justify-between group"
              >
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase">Active Course</span>
                  <h4 className="text-base font-bold text-white group-hover:text-indigo-400 transition-colors">
                    {e.course?.title}
                  </h4>
                </div>
                
                {/* Progress */}
                <div className="mt-6 space-y-2">
                  <div className="flex justify-between text-xs text-slate-500 font-semibold">
                    <span>Complete</span>
                    <span>{Math.round(e.progress_percent)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                      style={{ width: `${e.progress_percent}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Popular Presets */}
      <div className="space-y-4 pt-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <PlusCircle className="w-5 h-5 text-purple-400" /> Popular Preset Roadmaps
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {popularTopics.map((topic) => (
            <div
              key={topic.name}
              onClick={() => navigate(`/roadmap/${topic.name.toLowerCase()}`)}
              className="glass-card p-6 flex gap-4 hover:border-purple-500/30 cursor-pointer group"
            >
              <div className="w-12 h-12 rounded-xl bg-slate-800/85 border border-slate-700/50 flex items-center justify-center shrink-0 group-hover:scale-105 transition-all">
                {topic.icon}
              </div>
              <div className="flex flex-col justify-between w-full">
                <div>
                  <h4 className="text-base font-bold text-white group-hover:text-purple-400 transition-colors">
                    {topic.name}
                  </h4>
                  <p className="text-xs text-slate-400 leading-relaxed mt-1">
                    {topic.desc}
                  </p>
                </div>
                <div className="flex items-center gap-1 text-xs font-semibold text-slate-500 group-hover:text-indigo-400 transition-colors mt-3">
                  Explore Roadmap <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
