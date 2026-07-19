import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Map, Sparkles, CheckCircle2, Circle, ChevronDown, 
  ChevronUp, Loader2, ArrowLeft, PlayCircle, Plus, FileText, X
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface StaticStep {
  id: number;
  topic: string;
  step_title: string;
  step_description: string | null;
  step_order: number;
}

interface DBStep {
  id: string; // UUID
  title: string;
  description: string | null;
  step_order: number;
  course_id: string;
}

interface Enrollment {
  id: string;
  course_id: string;
  course: {
    id: string;
    title: string;
  } | null;
  progress_percent: number;
}

interface ProgressStatus {
  enrollment_id: string;
  completed_step_ids: string[];
  progress_percent: number;
}

export default function RoadmapPage() {
  const { topic } = useParams<{ topic: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});
  
  // Note Modal states
  const [noteModalOpen, setNoteModalOpen] = useState(false);
  const [noteModalStepId, setNoteModalStepId] = useState('');
  const [noteModalStepTitle, setNoteModalStepTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');

  // 1. Fetch public/static roadmap steps (works even if not enrolled)
  const { data: staticSteps, isLoading: staticLoading } = useQuery<StaticStep[]>({
    queryKey: ['staticRoadmap', topic],
    queryFn: async () => {
      if (!topic) return [];
      const res = await apiClient.get(`/roadmap/${encodeURIComponent(topic.toLowerCase())}`);
      return res.data;
    },
    enabled: !!topic,
  });

  // 2. Fetch user's enrollments to check if they are enrolled in this topic
  const { data: enrollmentList, isLoading: enrollmentsLoading } = useQuery<{ items: Enrollment[] }>({
    queryKey: ['userEnrollments'],
    queryFn: async () => {
      const res = await apiClient.get('/enrollments');
      return res.data;
    }
  });

  // Find matching enrollment
  const activeEnrollment = enrollmentList?.items.find(
    (e) => e.course?.title.toLowerCase() === topic?.toLowerCase()
  );

  // 3. If enrolled, fetch DB steps for this course
  const { data: dbSteps, isLoading: dbStepsLoading } = useQuery<{ items: DBStep[] }>({
    queryKey: ['courseSteps', activeEnrollment?.course_id],
    queryFn: async () => {
      const res = await apiClient.get(`/roadmap-steps?course_id=${activeEnrollment?.course_id}`);
      return res.data;
    },
    enabled: !!activeEnrollment?.course_id,
  });

  // 4. If enrolled, fetch step completion status
  const { data: progressStatus, isLoading: progressLoading } = useQuery<ProgressStatus>({
    queryKey: ['progressStatus', activeEnrollment?.id],
    queryFn: async () => {
      const res = await apiClient.get(`/progress/status/${activeEnrollment?.id}`);
      return res.data;
    },
    enabled: !!activeEnrollment?.id,
  });

  // 5. Toggle step completion mutation (with Optimistic Updates)
  const toggleStepMutation = useMutation({
    mutationFn: async ({ stepId, completed }: { stepId: string; completed: boolean }) => {
      await apiClient.post('/progress', {
        enrollment_id: activeEnrollment?.id,
        step_id: stepId,
        completed
      });
    },
    onMutate: async ({ stepId, completed }) => {
      await queryClient.cancelQueries({ queryKey: ['progressStatus', activeEnrollment?.id] });
      const previousProgress = queryClient.getQueryData<ProgressStatus>(['progressStatus', activeEnrollment?.id]);

      queryClient.setQueryData<ProgressStatus>(['progressStatus', activeEnrollment?.id], (old) => {
        if (!old) return old;
        const nextCompletedIds = completed
          ? [...old.completed_step_ids, stepId]
          : old.completed_step_ids.filter(id => id !== stepId);
        
        const totalCount = dbSteps?.items?.length || 1;
        const nextPercent = (nextCompletedIds.length / totalCount) * 100;
        
        return {
          ...old,
          completed_step_ids: nextCompletedIds,
          progress_percent: nextPercent
        };
      });

      return { previousProgress };
    },
    onError: (_err: any, _, context) => {
      if (context?.previousProgress) {
        queryClient.setQueryData(['progressStatus', activeEnrollment?.id], context.previousProgress);
      }
      toast.error('Failed to update progress.');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
      toast.success('Progress updated!');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['progressStatus', activeEnrollment?.id] });
      queryClient.invalidateQueries({ queryKey: ['userEnrollments'] });
    }
  });

  // Create note mutation
  const createNoteMutation = useMutation({
    mutationFn: async ({ stepId, content }: { stepId: string; content: string }) => {
      const res = await apiClient.post('/notes', { step_id: stepId, content });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userNotes'] });
      toast.success('Note added successfully!');
      setNoteModalOpen(false);
      setNoteContent('');
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || 'Failed to create note.';
      toast.error(msg);
    }
  });

  const handleOpenNoteModal = (stepId: string, title: string) => {
    setNoteModalStepId(stepId);
    setNoteModalStepTitle(title);
    setNoteContent('');
    setNoteModalOpen(true);
  };

  // 6. Enroll and create course roadmap steps mutation
  const enrollMutation = useMutation({
    mutationFn: async () => {
      if (!topic || !staticSteps || staticSteps.length === 0) return;

      // a. Get or Create Category
      let categoryId = '';
      const catListRes = await apiClient.get('/categories');
      if (catListRes.data.items && catListRes.data.items.length > 0) {
        categoryId = catListRes.data.items[0].id;
      } else {
        const createCatRes = await apiClient.post('/categories', {
          name: 'Software Development',
          description: 'General tracks for developers.'
        });
        categoryId = createCatRes.data.id;
      }

      // b. Create Course
      const courseRes = await apiClient.post('/courses', {
        title: topic.charAt(0).toUpperCase() + topic.slice(1),
        description: `Self-guided aggregation course for learning ${topic}.`,
        instructor_name: 'LearnHub System',
        difficulty_level: 'Beginner',
        duration_hours: staticSteps.length * 2,
        category_id: categoryId
      });
      const courseId = courseRes.data.id;

      // c. Create Roadmap Steps
      for (const step of staticSteps) {
        await apiClient.post('/roadmap-steps', {
          title: step.step_title,
          description: step.step_description || `Learn details about ${step.step_title}`,
          step_order: step.step_order,
          course_id: courseId
        });
      }

      // d. Create Enrollment
      await apiClient.post('/enrollments', {
        course_id: courseId
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userEnrollments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
      toast.success('Enrolled! Roadmap is now interactive.');
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || 'Failed to start learning path.';
      toast.error(msg);
    }
  });

  const toggleExpand = (id: string | number) => {
    const key = String(id);
    setExpandedSteps(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleStepToggle = (stepId: string, isCompleted: boolean) => {
    if (toggleStepMutation.isPending) return;
    toggleStepMutation.mutate({ stepId, completed: !isCompleted });
  };

  // Loading States
  const isGlobalLoading = staticLoading || enrollmentsLoading || dbStepsLoading || progressLoading;

  if (!topic) {
    return (
      <div className="text-center py-20">
        <Map className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white">No Topic Selected</h2>
        <button onClick={() => navigate('/dashboard')} className="mt-4 px-4 py-2 bg-indigo-600 rounded-xl text-sm font-semibold">
          Dashboard
        </button>
      </div>
    );
  }

  // Render static roadmap list if not enrolled
  const renderSteps = activeEnrollment && dbSteps?.items 
    ? dbSteps.items.sort((a, b) => a.step_order - b.step_order)
    : staticSteps?.sort((a, b) => a.step_order - b.step_order) || [];

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      
      {/* Header Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {/* Hero Header Area */}
      <div className="relative overflow-hidden rounded-3xl bg-slate-900 border border-slate-800 p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-1 bg-slate-850 px-2.5 py-1 rounded-md text-xs font-semibold text-indigo-400 border border-slate-700/50">
            <Sparkles className="w-3.5 h-3.5" /> Interactive Roadmap
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white capitalize">
            {topic} Roadmap
          </h1>
          <p className="text-slate-400 text-xs md:text-sm max-w-xl">
            A step-by-step guideline compiled to help you master {topic} concepts in the correct order.
          </p>
        </div>

        {/* Enrollment Control Panel */}
        <div className="relative z-10 shrink-0 w-full md:w-48">
          {activeEnrollment ? (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-widest flex justify-between">
                <span>Progress</span>
                <span>{Math.round(progressStatus?.progress_percent ?? activeEnrollment.progress_percent)}%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div 
                  className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressStatus?.progress_percent ?? activeEnrollment.progress_percent}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          ) : (
            <button
              onClick={() => enrollMutation.mutate()}
              disabled={enrollMutation.isPending}
              className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-850 text-white rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/15 flex items-center gap-2"
            >
              {enrollMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Starting Path...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" /> Enroll & Track Progress
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {isGlobalLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <p className="text-sm text-slate-500">Loading learning timeline...</p>
        </div>
      ) : renderSteps.length > 0 ? (
        <div className="relative border-l-2 border-slate-800 ml-4 md:ml-8 pl-6 md:pl-10 space-y-8 py-4">
          {renderSteps.map((step, idx) => {
            const stepId = 'id' in step ? String(step.id) : String(idx);
            const isCompleted = activeEnrollment && progressStatus?.completed_step_ids?.includes(stepId);
            const isExpanded = !!expandedSteps[stepId];
            
            // Extract details safely
            const title = 'step_title' in step ? step.step_title : (step as DBStep).title;
            const description = 'step_description' in step ? step.step_description : (step as DBStep).description;

            return (
              <div key={stepId} className="relative group">
                
                {/* Node Dot icon */}
                <div className="absolute -left-[35px] md:-left-[51px] top-1.5 z-10 flex items-center justify-center w-6 h-6 md:w-8 md:h-8 rounded-full bg-slate-950 border-2 border-slate-800 group-hover:border-slate-700 transition-colors">
                  {activeEnrollment ? (
                    <button 
                      onClick={() => handleStepToggle(stepId, !!isCompleted)}
                      disabled={toggleStepMutation.isPending}
                      className="w-full h-full flex items-center justify-center rounded-full hover:bg-slate-900 transition-colors"
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-4 h-4 md:w-5 h-5 text-emerald-500 fill-emerald-500/10" />
                      ) : (
                        <Circle className="w-4 h-4 md:w-5 h-5 text-slate-600 hover:text-indigo-400" />
                      )}
                    </button>
                  ) : (
                    <span className="text-[10px] md:text-xs font-bold text-slate-500">
                      {idx + 1}
                    </span>
                  )}
                </div>

                {/* Step Card */}
                <div className="glass-card p-5 hover:border-slate-700/60 flex flex-col gap-3">
                  <div 
                    onClick={() => toggleExpand(stepId)}
                    className="flex justify-between items-center cursor-pointer"
                  >
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold text-indigo-400 tracking-widest uppercase">
                        Step {idx + 1}
                      </span>
                      <h4 className={`text-base font-bold text-white transition-all ${isCompleted ? 'line-through text-slate-500' : ''}`}>
                        {title}
                      </h4>
                    </div>
                    {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                  </div>

                  {/* Expandable details */}
                  <AnimatePresence initial={false}>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <p className="text-sm text-slate-400 leading-relaxed pt-2 border-t border-slate-800/80 mt-2">
                          {description || 'Explore aggregated resources on your search dashboard to learn this step.'}
                        </p>
                        
                        {/* Quick study resource button shortcut */}
                        <div className="mt-4 flex gap-3">
                          <button
                            onClick={() => navigate(`/search?q=${encodeURIComponent(title)}`)}
                            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 hover:text-white transition-all flex items-center gap-1.5"
                          >
                            <PlayCircle className="w-4 h-4 text-purple-400" /> Find Videos & Repos
                          </button>
                          {activeEnrollment && (
                            <button
                              onClick={() => handleOpenNoteModal(stepId, title)}
                              className="px-3.5 py-1.5 rounded-lg bg-indigo-650/15 hover:bg-indigo-600/30 border border-indigo-500/20 text-xs font-semibold text-indigo-400 transition-all flex items-center gap-1.5"
                            >
                              <FileText className="w-4 h-4 text-indigo-400" /> Add Note
                            </button>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-20 border border-dashed border-slate-800 rounded-2xl">
          <Map className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-500">No static steps found for this topic roadmap.</p>
        </div>
      )}

      {/* Note Modal */}
      <AnimatePresence>
        {noteModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setNoteModalOpen(false)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            {/* Dialog Card */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 space-y-6 shadow-2xl overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-44 h-44 bg-indigo-500/10 rounded-full blur-[50px] pointer-events-none" />
              
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 relative z-10">
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-white">Add Study Note</h3>
                  <p className="text-xs text-slate-400">Step: {noteModalStepTitle}</p>
                </div>
                <button 
                  onClick={() => setNoteModalOpen(false)}
                  className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4 relative z-10">
                <textarea
                  autoFocus
                  placeholder="Type your summary, cheat sheet reference, or markdown note details here..."
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  className="w-full h-44 bg-slate-950/50 border border-slate-700/60 focus-glow rounded-xl p-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none resize-none font-sans leading-relaxed"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2 relative z-10">
                <button
                  type="button"
                  onClick={() => setNoteModalOpen(false)}
                  className="px-4 py-2 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-400 hover:text-slate-250 rounded-xl transition-all"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => createNoteMutation.mutate({ stepId: noteModalStepId, content: noteContent.trim() })}
                  disabled={createNoteMutation.isPending || !noteContent.trim()}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-850 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/15 flex items-center gap-1.5 transition-all"
                >
                  {createNoteMutation.isPending ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    'Save Note'
                  )}
                </button>
              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
