import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function PlaceholderPage({ title }: { title: string }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-6">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 glass-card p-10 max-w-lg w-full flex flex-col items-center">
        <h1 className="text-3xl font-extrabold text-white mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          {title}
        </h1>
        <p className="text-slate-400 mb-8 leading-relaxed">
          This is a placeholder for the <span className="text-white font-medium">{title}</span> feature. We are currently implementing Phase 1 (Foundation & Landing Page) checkpoint-by-checkpoint.
        </p>
        
        {location.search && (
          <div className="w-full text-left bg-slate-800/80 border border-slate-700/50 p-4 rounded-xl mb-6 text-sm text-slate-300 font-mono">
            Query parameters: {location.search}
          </div>
        )}

        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-all border border-slate-700/80 hover:border-slate-600 shadow-md"
        >
          <ArrowLeft className="w-4 h-4" /> Go Back to Home
        </button>
      </div>
    </div>
  );
}
