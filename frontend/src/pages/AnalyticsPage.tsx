import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3, Hourglass, CheckCircle2, Award, Loader2, BookOpen } from 'lucide-react';

interface CategoryDistribution {
  category_name: string;
  enrolled_courses_count: number;
  average_progress_percent: number;
}

interface CourseDetail {
  course_id: string;
  course_title: string;
  total_steps_count: number;
  completed_steps_count: number;
  progress_percent: number;
  duration_hours: number;
  is_completed: boolean;
}

interface AnalyticsResponse {
  total_study_hours_committed: number;
  overall_average_progress: number;
  category_distribution: CategoryDistribution[];
  course_details: CourseDetail[];
}

const COLORS = ['#4F46E5', '#7C3AED', '#06B6D4', '#22C55E', '#F59E0B'];

export default function AnalyticsPage() {
  // Fetch detailed student learning analytics
  const { data, isLoading, error } = useQuery<AnalyticsResponse>({
    queryKey: ['studentAnalytics'],
    queryFn: async () => {
      const res = await apiClient.get('/analytics/overview');
      return res.data;
    }
  });

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Detailed Learning Analytics <BarChart3 className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Track category coverage distributions, cumulative study hours, and individual course milestones.
        </p>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <p className="text-sm text-slate-500">Retrieving study records...</p>
        </div>
      ) : error ? (
        <div className="text-center py-10 bg-rose-500/10 border border-rose-500/20 rounded-2xl max-w-xl mx-auto">
          <p className="text-rose-400 font-semibold">Failed to fetch study analytics</p>
        </div>
      ) : (
        <div className="space-y-8">
          
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 shrink-0">
                <Hourglass className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-400">Total Hours Committed</div>
                <div className="text-2xl font-extrabold text-white mt-1">
                  {data?.total_study_hours_committed ?? 0} hrs
                </div>
              </div>
            </div>

            <div className="glass-card p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 shrink-0">
                <BarChart3 className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-400">Average Course Progress</div>
                <div className="text-2xl font-extrabold text-white mt-1">
                  {Math.round(data?.overall_average_progress ?? 0)}%
                </div>
              </div>
            </div>

            <div className="glass-card p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0">
                <Award className="w-6 h-6" />
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-400">Completed Courses</div>
                <div className="text-2xl font-extrabold text-white mt-1">
                  {data?.course_details.filter(c => c.is_completed).length ?? 0} / {data?.course_details.length ?? 0}
                </div>
              </div>
            </div>
          </div>

          {/* Category Distribution Chart */}
          {data?.category_distribution && data.category_distribution.length > 0 && (
            <div className="glass-card p-6 md:p-8 space-y-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-400" /> Category Progress Distribution
              </h3>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.category_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="category_name" stroke="#94A3B8" fontSize={11} tickLine={false} />
                    <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ background: '#1E293B', border: '1px solid rgba(100,116,139,0.2)', borderRadius: '8px' }}
                      labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                      itemStyle={{ color: '#818CF8' }}
                    />
                    <Bar dataKey="average_progress_percent" radius={[4, 4, 0, 0]}>
                      {data.category_distribution.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Detailed Course Breakdown */}
          <div className="glass-card p-6 md:p-8 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-purple-400" /> Roadmap Milestones Breakdown
            </h3>

            {data?.course_details && data.course_details.length > 0 ? (
              <div className="divide-y divide-slate-800/80">
                {data.course_details.map((course) => (
                  <div key={course.course_id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 first:pt-0 last:pb-0">
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-white">{course.course_title}</h4>
                      <p className="text-xs text-slate-500">
                        Completed {course.completed_steps_count} of {course.total_steps_count} steps &bull; {course.duration_hours} hrs committed
                      </p>
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                        course.is_completed 
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                          : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                      }`}>
                        {course.is_completed ? 'Finished' : 'In Progress'}
                      </span>
                      <span className="text-sm font-bold text-white w-10 text-right">
                        {Math.round(course.progress_percent)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10 text-sm text-slate-500">
                No active courses to display breakdown metrics.
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
