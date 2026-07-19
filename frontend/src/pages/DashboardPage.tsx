import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api';
import { motion } from 'framer-motion';
import { 
  BookOpen, Bookmark, CheckCircle, 
  Hourglass, Search, ChevronRight, TrendingUp, Sparkles 
} from 'lucide-react';

interface ActiveCourseProgress {
  enrollment_id: string;
  course_id: string;
  course_title: string;
  progress_percent: number;
  enrolled_at: string;
  completed_at: string | null;
}

interface DashboardMetrics {
  total_enrolled: number;
  in_progress_count: number;
  completed_count: number;
  total_bookmarks: number;
  total_notes: number;
  recent_courses: ActiveCourseProgress[];
}

interface TrendingTopic {
  query: string;
  count: number;
}

interface TrendingResponse {
  total_searches: number;
  trending_topics: TrendingTopic[];
}

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // 1. Fetch dashboard metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery<DashboardMetrics>({
    queryKey: ['dashboardMetrics'],
    queryFn: async () => {
      const res = await apiClient.get('/dashboard/metrics');
      return res.data;
    }
  });

  // 2. Fetch trending searches for popular shortcuts
  const { data: trendingData, isLoading: trendingLoading } = useQuery<TrendingResponse>({
    queryKey: ['globalTrending'],
    queryFn: async () => {
      const res = await apiClient.get('/analytics');
      return res.data;
    }
  });

  const handleShortcutClick = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  const handleSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const q = fd.get('q') as string;
    if (q?.trim()) {
      navigate(`/search?q=${encodeURIComponent(q.trim())}`);
    }
  };

  const stats = [
    { 
      label: 'Enrolled Courses', 
      value: metrics?.total_enrolled ?? 0, 
      icon: <BookOpen className="w-5 h-5 text-indigo-400" />,
      colorClass: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10'
    },
    { 
      label: 'In Progress', 
      value: metrics?.in_progress_count ?? 0, 
      icon: <Hourglass className="w-5 h-5 text-purple-400" />,
      colorClass: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    { 
      label: 'Completed', 
      value: metrics?.completed_count ?? 0, 
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />,
      colorClass: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10'
    },
    { 
      label: 'Bookmarks', 
      value: metrics?.total_bookmarks ?? 0, 
      icon: <Bookmark className="w-5 h-5 text-cyan-400" />,
      colorClass: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10'
    }
  ];

  return (
    <div className="space-y-8">
      
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900 border border-slate-800 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <h1 className="text-3xl md:text-4xl font-extrabold text-white flex items-center gap-3">
              Welcome back, {user?.full_name || 'Student'}! <Sparkles className="w-6 h-6 text-yellow-400 animate-pulse" />
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-xl">
              Ready to explore? search a new topic to generate a roadmap or continue where you left off.
            </p>
          </div>
          
          {/* Quick Search */}
          <form onSubmit={handleSearchSubmit} className="w-full md:max-w-xs shrink-0">
            <div className="relative">
              <Search className="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                name="q"
                placeholder="Search learning topics..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus-glow text-sm"
              />
            </div>
          </form>
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
        {stats.map((stat, idx) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: idx * 0.05 }}
            whileHover={{ y: -4 }}
            className="glass-card p-5 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs md:text-sm font-medium text-slate-400">{stat.label}</span>
              <div className={`w-8 h-8 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                {stat.icon}
              </div>
            </div>
            {metricsLoading ? (
              <div className="h-8 w-16 bg-slate-800/80 rounded-md animate-pulse" />
            ) : (
              <span className="text-2xl md:text-3xl font-extrabold text-white">{stat.value}</span>
            )}
          </motion.div>
        ))}
      </div>

      {/* Main Grid: Continue Learning & Popular Topics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Continue Learning Widget (2 columns) */}
        <div className="lg:col-span-2 glass-card p-6 md:p-8 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-400" /> Continue Learning
            </h2>
            <button 
              onClick={() => navigate('/roadmap')}
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
            >
              All Roadmaps <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {metricsLoading ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="h-16 w-full bg-slate-800/50 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : metrics?.recent_courses && metrics.recent_courses.length > 0 ? (
            <div className="space-y-4">
              {metrics.recent_courses.map((course) => (
                <div 
                  key={course.enrollment_id}
                  onClick={() => navigate(`/roadmap/${course.course_title.toLowerCase()}`)}
                  className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/30 hover:bg-slate-900/60 hover:border-slate-700/60 transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <h4 className="text-sm font-bold text-white">{course.course_title}</h4>
                    <p className="text-xs text-slate-500">
                      Enrolled: {new Date(course.enrolled_at).toLocaleDateString()}
                    </p>
                  </div>
                  
                  {/* Progress bar container */}
                  <div className="flex items-center gap-3 w-full md:max-w-xs">
                    <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${course.progress_percent}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                      />
                    </div>
                    <span className="text-xs font-bold text-slate-300 shrink-0">
                      {Math.round(course.progress_percent)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-10 border border-dashed border-slate-800 rounded-2xl">
              <BookOpen className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500">You haven't enrolled in any courses yet.</p>
              <button 
                onClick={() => navigate('/search')}
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md transition-colors"
              >
                Find Resources
              </button>
            </div>
          )}
        </div>

        {/* Global Trending Shortcuts (1 column) */}
        <div className="glass-card p-6 md:p-8 space-y-6">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" /> Trending Topics
          </h2>

          {trendingLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 w-full bg-slate-800/50 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : trendingData?.trending_topics && trendingData.trending_topics.length > 0 ? (
            <div className="flex flex-col gap-2">
              {trendingData.trending_topics.slice(0, 5).map((topic, index) => (
                <button
                  key={topic.query}
                  onClick={() => handleShortcutClick(topic.query)}
                  className="flex items-center justify-between p-3 rounded-xl border border-slate-800 hover:border-slate-700/80 bg-slate-900/40 hover:bg-slate-850 text-left text-sm text-slate-300 hover:text-white transition-all group"
                >
                  <span className="truncate flex items-center gap-2 font-medium">
                    <span className="text-xs text-slate-600 font-bold w-4">#{index + 1}</span>
                    {topic.query}
                  </span>
                  <span className="text-xs text-slate-500 font-semibold group-hover:text-indigo-400 transition-colors">
                    {topic.count} searches
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-sm text-slate-500">
              No queries logged yet.
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
