import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Code, Video, BookOpen, Database, 
  FileText, ExternalLink, Star, GitFork, Book, 
  Map, Sparkles, HelpCircle, Loader2, BookmarkPlus, BookmarkCheck
} from 'lucide-react';

interface BookmarkItem {
  id: string;
  resource_id: string;
  created_at: string;
  resource: {
    title: string;
    url: string;
    type: string;
    step_id: string;
  } | null;
}

interface Course {
  id: number | null;
  title: string;
  url: string;
  description: string | null;
  source: string;
}

interface Repository {
  id: number | null;
  name: string;
  full_name: string;
  url: string;
  description: string | null;
  stars: number;
  forks: number;
  language: string | null;
}

interface VideoItem {
  id: number | null;
  title: string;
  video_id: string;
  url: string;
  description: string | null;
  thumbnail: string | null;
  channel_title: string | null;
  published_at: string | null;
}

interface BookItem {
  id: number | null;
  title: string;
  authors: string | null;
  description: string | null;
  thumbnail: string | null;
  info_link: string;
  publisher: string | null;
  published_date: string | null;
}

interface Dataset {
  id: number | null;
  title: string;
  url: string;
  description: string | null;
  size: string | null;
  creator: string | null;
}

interface SearchResponse {
  course: Course | null;
  category?: string;
  roadmap: Array<{
    step_title: string;
    step_description: string;
    step_order: number;
    resources: {
      videos: VideoItem[];
      books: BookItem[];
      repositories: Repository[];
      datasets: Dataset[];
      documentation: any[];
    };
  }>;
  repositories: Repository[];
  videos: VideoItem[];
  books: BookItem[];
  datasets: Dataset[];
  documentation: Array<{ title: string; url: string; description?: string }>;
  last_updated: string;
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryParam = searchParams.get('q') || '';
  
  const [searchInput, setSearchInput] = useState(queryParam);
  const [activeTab, setActiveTab] = useState<'overview' | 'repos' | 'videos' | 'books' | 'datasets' | 'docs'>('overview');
  const queryClient = useQueryClient();

  useEffect(() => {
    setSearchInput(queryParam);
  }, [queryParam]);

  // Query search results
  const { data, isLoading, error, isFetching } = useQuery<SearchResponse>({
    queryKey: ['searchTopic', queryParam],
    queryFn: async () => {
      if (!queryParam) return {
        course: null, roadmap: [], repositories: [], videos: [], books: [], datasets: [], documentation: [], last_updated: ''
      };
      const res = await apiClient.get(`/search?query=${encodeURIComponent(queryParam)}`);
      return res.data;
    },
    enabled: !!queryParam,
  });


  const { data: userBookmarks } = useQuery<{ items: BookmarkItem[] }>({
    queryKey: ['userBookmarks'],
    queryFn: async () => {
      const res = await apiClient.get('/bookmarks');
      return res.data;
    }
  });

  const bookmarkMutation = useMutation({
    mutationFn: async (item: { title: string; url: string; type: string }) => {
      const res = await apiClient.post('/bookmarks/external', item);
      return res.data;
    },
    onMutate: async (newBookmarkItem) => {
      await queryClient.cancelQueries({ queryKey: ['userBookmarks'] });
      const previousBookmarks = queryClient.getQueryData<{ items: BookmarkItem[] }>(['userBookmarks']);

      queryClient.setQueryData<{ items: BookmarkItem[] }>(['userBookmarks'], (old) => {
        const tempBookmark: BookmarkItem = {
          id: 'temp-id-' + Date.now(),
          resource_id: 'temp-res-id',
          created_at: new Date().toISOString(),
          resource: {
            title: newBookmarkItem.title,
            url: newBookmarkItem.url,
            type: newBookmarkItem.type,
            step_id: ''
          }
        };
        return {
          items: old?.items ? [tempBookmark, ...old.items] : [tempBookmark]
        };
      });

      return { previousBookmarks };
    },
    onError: (err: any, _, context) => {
      if (context?.previousBookmarks) {
        queryClient.setQueryData(['userBookmarks'], context.previousBookmarks);
      }
      const msg = err.response?.data?.detail || 'Failed to save bookmark.';
      toast.error(msg);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
      toast.success('Saved to bookmarks.');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['userBookmarks'] });
    }
  });

  const handleBookmark = (item: { title: string; url: string; type: string }) => {
    // Prevent duplicate bookmarks checking
    const exists = userBookmarks?.items?.some(b => b.resource?.url === item.url);
    if (exists) {
      toast.error('Resource is already bookmarked.');
      return;
    }
    if (bookmarkMutation.isPending) return;
    bookmarkMutation.mutate(item);
  };
  const isBookmarked = (url: string) => userBookmarks?.items?.some(b => b.resource?.url === url) || false;
  const isSaving = (url: string) => bookmarkMutation.isPending && bookmarkMutation.variables?.url === url;

  const handleSearchSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSearchParams({ q: searchInput.trim() });
    }
  };

  const handleEnrollOrRoadmap = () => {
    if (queryParam) {
      navigate(`/roadmap/${encodeURIComponent(queryParam.toLowerCase())}`);
    }
  };

  // Skeleton Loader for cards
  const CardSkeleton = () => (
    <div className="glass-card p-5 space-y-4 animate-pulse">
      <div className="h-4 bg-slate-800 rounded-md w-2/3" />
      <div className="space-y-2">
        <div className="h-3 bg-slate-800 rounded-md w-full" />
        <div className="h-3 bg-slate-800 rounded-md w-5/6" />
      </div>
      <div className="flex gap-3 pt-2">
        <div className="h-6 w-16 bg-slate-800 rounded-full" />
        <div className="h-6 w-16 bg-slate-800 rounded-full" />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      
      {/* Search Header Area */}
      <div className="flex flex-col gap-4">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Aggregated Search Results <Search className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Queries external developer repositories, learning guides, public books, videos, and datasets concurrently.
        </p>

        {/* Input Bar */}
        <form onSubmit={handleSearchSubmit} className="w-full max-w-2xl mt-2">
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 rounded-xl blur opacity-25 group-hover:opacity-35 transition duration-1000 group-focus-within:opacity-40" />
            <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-xl">
              <Search className="w-5 h-5 text-slate-500 ml-4 pointer-events-none" />
              <input
                type="text"
                placeholder="What do you want to learn?"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full bg-transparent px-4 py-3.5 text-slate-100 placeholder-slate-500 focus:outline-none text-sm"
              />
              <button
                type="submit"
                disabled={isFetching}
                className="mr-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs px-4 py-2 rounded-lg transition-all shadow-md flex items-center gap-1.5"
              >
                {isFetching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Discover My Path'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {!queryParam && (
        <div className="text-center py-20 border border-dashed border-slate-800 rounded-2xl max-w-2xl mx-auto">
          <HelpCircle className="w-10 h-10 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Topic Specified</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Please enter a learning keyword in the search bar above to fetch resources dynamically from the API cache.
          </p>
        </div>
      )}

      {error && (
        <div className="text-center py-10 bg-rose-500/10 border border-rose-500/20 rounded-2xl max-w-xl mx-auto">
          <p className="text-rose-400 font-semibold mb-2">Aggregation Failed</p>
          <p className="text-xs text-rose-500">Please confirm backend is running or query is valid.</p>
        </div>
      )}

      {queryParam && !error && (
        <>
          {/* Skill Title & Category */}
          {!isLoading && data && (
            <div className="flex flex-col gap-1 my-4">
              <h2 className="text-3xl font-extrabold text-white capitalize">{queryParam}</h2>
              <span className="text-sm text-indigo-400 font-semibold">Category: {data.category || "Other"}</span>
            </div>
          )}

          {/* Main Course Hero Card (If present in Search results) */}
          {isLoading ? (
            <div className="h-44 w-full bg-slate-900/60 border border-slate-800/80 rounded-3xl animate-pulse" />
          ) : data?.course && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/20 via-slate-900 to-slate-900 border border-slate-800 p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              <div className="space-y-3">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-semibold text-indigo-400">
                  <Sparkles className="w-3.5 h-3.5" /> Best Learning Match
                </div>
                <h2 className="text-2xl font-extrabold text-white">{data.course.title}</h2>
                <p className="text-sm text-slate-400 max-w-xl leading-relaxed">
                  {data.course.description || "We found a matching core curriculum on our backend. View the interactive vertical roadmap timeline or begin studying now."}
                </p>
              </div>
              <button
                onClick={handleEnrollOrRoadmap}
                className="shrink-0 px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-indigo-600/20 flex items-center gap-2"
              >
                <Map className="w-4 h-4" /> View Interactive Roadmap
              </button>
            </motion.div>
          )}

          {/* Learning Roadmap with Mapped Resources */}
          {!isLoading && data?.roadmap && data.roadmap.length > 0 && (
            <div className="space-y-4 my-8">
              <h3 className="text-xl font-extrabold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
                <Map className="w-5 h-5 text-indigo-400" /> Learning Roadmap
              </h3>
              <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
                {data.roadmap.map((step, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-[35px] top-1.5 z-10 flex items-center justify-center w-6 h-6 rounded-full bg-slate-950 border-2 border-indigo-500 text-xs font-bold text-slate-300">
                      {step.step_order}
                    </div>
                    <div className="glass-card p-5 space-y-3">
                      <h4 className="text-base font-bold text-white leading-snug">
                        {step.step_title}
                      </h4>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {step.step_description}
                      </p>
                      
                      {/* Mapped Resources for Stage */}
                      <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                          Resources for this stage:
                        </span>
                        
                        {(!step.resources || 
                          (step.resources.videos.length === 0 && 
                           step.resources.books.length === 0 && 
                           step.resources.repositories.length === 0 && 
                           step.resources.datasets.length === 0 &&
                           step.resources.documentation.length === 0)) ? (
                          <p className="text-xs text-slate-500 italic">No specific resource mapped to this stage.</p>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
                            {step.resources.videos.map((v, index) => (
                              <div key={index} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50 text-xs">
                                <span className="text-slate-300 truncate max-w-[200px]" title={v.title}>🎥 {v.title}</span>
                                <a href={v.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 ml-2 shrink-0">Open</a>
                              </div>
                            ))}
                            {step.resources.books.map((b, index) => (
                              <div key={index} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50 text-xs">
                                <span className="text-slate-300 truncate max-w-[200px]" title={b.title}>📖 {b.title}</span>
                                <a href={b.info_link} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 ml-2 shrink-0">Open</a>
                              </div>
                            ))}
                            {step.resources.repositories.map((r, index) => (
                              <div key={index} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50 text-xs">
                                <span className="text-slate-300 truncate max-w-[200px]" title={r.name}>💻 {r.name}</span>
                                <a href={r.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 ml-2 shrink-0">Open</a>
                              </div>
                            ))}
                            {step.resources.datasets.map((d, index) => (
                              <div key={index} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50 text-xs">
                                <span className="text-slate-300 truncate max-w-[200px]" title={d.title}>📊 {d.title}</span>
                                <a href={d.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 ml-2 shrink-0">Open</a>
                              </div>
                            ))}
                            {step.resources.documentation.map((dc, index) => (
                              <div key={index} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50 text-xs">
                                <span className="text-slate-300 truncate max-w-[200px]" title={dc.title}>📄 {dc.title}</span>
                                <a href={dc.url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 ml-2 shrink-0">Open</a>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Resources Heading */}
          {!isLoading && data && (
            <h3 className="text-lg font-bold text-white mb-3">Recommended Resources</h3>
          )}

          {/* Navigation Filter Tabs */}
          <div className="flex overflow-x-auto gap-2 pb-2 border-b border-slate-800/85 scrollbar-thin">
            {[
              { id: 'overview', name: 'Overview', icon: <Sparkles className="w-4 h-4" />, show: true },
              { id: 'repos', name: 'Repositories', icon: <Code className="w-4 h-4" />, show: data?.repositories && data.repositories.length > 0 },
              { id: 'videos', name: 'Videos', icon: <Video className="w-4 h-4" />, show: data?.videos && data.videos.length > 0 },
              { id: 'books', name: 'Books', icon: <BookOpen className="w-4 h-4" />, show: data?.books && data.books.length > 0 },
              { id: 'datasets', name: 'Datasets', icon: <Database className="w-4 h-4" />, show: data?.datasets && data.datasets.length > 0 },
              { id: 'docs', name: 'Documentation', icon: <FileText className="w-4 h-4" />, show: data?.documentation && data.documentation.length > 0 },
            ].filter(tab => tab.show).map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                  activeTab === tab.id
                    ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-400 hover:text-slate-200 bg-slate-900/40 border border-transparent'
                }`}
              >
                {tab.icon}
                {tab.name}
              </button>
            ))}
          </div>

          {/* Results Views */}
          <div className="mt-6">
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => <CardSkeleton key={i} />)}
              </div>
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  
                  {/* T1. Overview Tab */}
                  {activeTab === 'overview' && (
                    <div className="space-y-10">
                      
                      {/* Top Repos */}
                      {data?.repositories && data.repositories.length > 0 && (
                        <div className="space-y-4">
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Code className="w-5 h-5 text-indigo-400" /> Featured GitHub Repositories
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {data.repositories.slice(0, 2).map((repo) => (
                              <RepoCard key={repo.full_name} repo={repo} onBookmark={handleBookmark} isBookmarked={isBookmarked(repo.url)} isSaving={isSaving(repo.url)} />
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Top Videos */}
                      {data?.videos && data.videos.length > 0 && (
                        <div className="space-y-4">
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Video className="w-5 h-5 text-purple-400" /> YouTube Tutorials
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {data.videos.slice(0, 2).map((video) => (
                              <VideoCard key={video.video_id} video={video} onBookmark={handleBookmark} isBookmarked={isBookmarked(video.url)} isSaving={isSaving(video.url)} />
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Top Books */}
                      {data?.books && data.books.length > 0 && (
                        <div className="space-y-4">
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <BookOpen className="w-5 h-5 text-cyan-400" /> Relevant Books & References
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {data.books.slice(0, 2).map((book) => (
                              <BookCard key={book.info_link} book={book} onBookmark={handleBookmark} isBookmarked={isBookmarked(book.info_link)} isSaving={isSaving(book.info_link)} />
                            ))}
                          </div>
                        </div>
                      )}

                    </div>
                  )}

                  {/* T2. Repositories Tab */}
                  {activeTab === 'repos' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {data?.repositories && data.repositories.length > 0 ? (
                        data.repositories.map((repo) => <RepoCard key={repo.full_name} repo={repo} onBookmark={handleBookmark} isBookmarked={isBookmarked(repo.url)} isSaving={isSaving(repo.url)} />)
                      ) : <EmptyState type="repositories" />}
                    </div>
                  )}

                  {/* T3. Videos Tab */}
                  {activeTab === 'videos' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {data?.videos && data.videos.length > 0 ? (
                        data.videos.map((video) => <VideoCard key={video.video_id} video={video} onBookmark={handleBookmark} isBookmarked={isBookmarked(video.url)} isSaving={isSaving(video.url)} />)
                      ) : <EmptyState type="videos" />}
                    </div>
                  )}

                  {/* T4. Books Tab */}
                  {activeTab === 'books' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {data?.books && data.books.length > 0 ? (
                        data.books.map((book) => <BookCard key={book.info_link} book={book} onBookmark={handleBookmark} isBookmarked={isBookmarked(book.info_link)} isSaving={isSaving(book.info_link)} />)
                      ) : <EmptyState type="books" />}
                    </div>
                  )}

                  {/* T5. Datasets Tab */}
                  {activeTab === 'datasets' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {data?.datasets && data.datasets.length > 0 ? (
                        data.datasets.map((ds) => <DatasetCard key={ds.url} ds={ds} onBookmark={handleBookmark} isBookmarked={isBookmarked(ds.url)} isSaving={isSaving(ds.url)} />)
                      ) : <EmptyState type="datasets" />}
                    </div>
                  )}

                  {/* T6. Documentation Tab */}
                  {activeTab === 'docs' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {data?.documentation && data.documentation.length > 0 ? (
                        data.documentation.map((doc) => <DocCard key={doc.url} doc={doc} onBookmark={handleBookmark} isBookmarked={isBookmarked(doc.url)} isSaving={isSaving(doc.url)} />)
                      ) : <EmptyState type="documentation" />}
                    </div>
                  )}

                </motion.div>
              </AnimatePresence>
            )}
          </div>
        </>
      )}

    </div>
  );
}

// Child Card Components to keep layout clean
type BookmarkPayload = { title: string; url: string; type: string };

function SaveButton({ onClick, isBookmarked, isSaving }: { onClick: () => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={isBookmarked || isSaving}
      className={`text-xs font-semibold flex items-center gap-1.5 transition-colors ${
        isBookmarked
          ? 'text-emerald-405 cursor-not-allowed text-emerald-400'
          : isSaving
          ? 'text-indigo-400 cursor-not-allowed'
          : 'text-indigo-300 hover:text-indigo-200'
      }`}
    >
      {isSaving ? (
        <>Saving <Loader2 className="w-3.5 h-3.5 animate-spin" /></>
      ) : isBookmarked ? (
        <>Saved <BookmarkCheck className="w-3.5 h-3.5 text-emerald-400" /></>
      ) : (
        <>Save <BookmarkPlus className="w-3.5 h-3.5" /></>
      )}
    </button>
  );
}

function RepoCard({ repo, onBookmark, isBookmarked, isSaving }: { repo: Repository; onBookmark: (item: BookmarkPayload) => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="glass-card p-5 flex flex-col justify-between group">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-md">
            {repo.language || 'Code'}
          </span>
          <div className="flex items-center gap-3 text-slate-400 text-xs">
            <span className="flex items-center gap-1"><Star className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" /> {repo.stars}</span>
            <span className="flex items-center gap-1"><GitFork className="w-3.5 h-3.5" /> {repo.forks}</span>
          </div>
        </div>
        <h4 className="text-base font-bold text-white group-hover:text-indigo-400 transition-colors leading-snug">
          {repo.name}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {repo.description || 'No description provided.'}
        </p>
      </div>
      <div className="pt-4 border-t border-slate-800/80 mt-4 flex items-center justify-between gap-3">
        <span className="text-[10px] text-slate-500 font-mono truncate max-w-[150px]">{repo.full_name}</span>
        <div className="flex items-center gap-3 shrink-0">
          <SaveButton onClick={() => onBookmark({ title: repo.name, url: repo.url, type: 'Repository' })} isBookmarked={isBookmarked} isSaving={isSaving} />
          <a 
            href={repo.url} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
          >
            Open <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}

function VideoCard({ video, onBookmark, isBookmarked, isSaving }: { video: VideoItem; onBookmark: (item: BookmarkPayload) => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="glass-card overflow-hidden flex flex-col justify-between group">
      <div>
        {video.thumbnail && (
          <div className="aspect-video w-full overflow-hidden bg-slate-950 relative border-b border-slate-800">
            <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-60" />
          </div>
        )}
        <div className="p-5 space-y-2">
          <h4 className="text-sm font-bold text-white group-hover:text-purple-400 transition-colors line-clamp-2 leading-snug">
            {video.title}
          </h4>
          <p className="text-xs text-slate-500">
            Channel: <span className="text-slate-400 font-medium">{video.channel_title || 'YouTube'}</span>
          </p>
        </div>
      </div>
      <div className="p-5 pt-0 mt-2 flex items-center justify-between gap-3 border-t border-slate-800/80">
        <span className="text-[10px] text-slate-600 font-mono">YouTube</span>
        <div className="flex items-center gap-3 shrink-0">
          <SaveButton onClick={() => onBookmark({ title: video.title, url: video.url, type: 'Video' })} isBookmarked={isBookmarked} isSaving={isSaving} />
          <a 
            href={video.url} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
          >
            Watch <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}

function BookCard({ book, onBookmark, isBookmarked, isSaving }: { book: BookItem; onBookmark: (item: BookmarkPayload) => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="glass-card p-5 flex gap-4 hover:border-cyan-500/30 group">
      {book.thumbnail ? (
        <div className="w-16 h-24 rounded-lg bg-slate-950 overflow-hidden shrink-0 border border-slate-800 shadow-md">
          <img src={book.thumbnail} alt={book.title} className="w-full h-full object-cover" />
        </div>
      ) : (
        <div className="w-16 h-24 rounded-lg bg-slate-950 flex items-center justify-center shrink-0 border border-slate-800 text-slate-600">
          <Book className="w-6 h-6" />
        </div>
      )}
      <div className="flex flex-col justify-between w-full min-w-0">
        <div className="space-y-1">
          <h4 className="text-sm font-bold text-white truncate group-hover:text-cyan-400 transition-colors leading-snug">
            {book.title}
          </h4>
          <p className="text-xs text-slate-400 truncate">
            {book.authors || 'Unknown Author'}
          </p>
          <p className="text-[10px] text-slate-500 truncate">
            Publisher: {book.publisher || 'Unknown'}
          </p>
        </div>
        <div className="flex items-center gap-3 mt-3">
          <SaveButton onClick={() => onBookmark({ title: book.title, url: book.info_link, type: 'Book' })} isBookmarked={isBookmarked} isSaving={isSaving} />
          <a 
            href={book.info_link} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            Open <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}

function DatasetCard({ ds, onBookmark, isBookmarked, isSaving }: { ds: Dataset; onBookmark: (item: BookmarkPayload) => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="glass-card p-5 flex flex-col justify-between group">
      <div className="space-y-2">
        <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md">
          {ds.size || 'Data'}
        </span>
        <h4 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors leading-snug">
          {ds.title}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-2">
          {ds.description || 'HuggingFace aggregated dataset.'}
        </p>
      </div>
      <div className="pt-4 border-t border-slate-800/80 mt-4 flex items-center justify-between gap-3">
        <span className="text-[10px] text-slate-500 truncate max-w-[120px]">Creator: {ds.creator || 'HF'}</span>
        <div className="flex items-center gap-3 shrink-0">
          <SaveButton onClick={() => onBookmark({ title: ds.title, url: ds.url, type: 'Dataset' })} isBookmarked={isBookmarked} isSaving={isSaving} />
          <a 
            href={ds.url} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5"
          >
            Open <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}

function DocCard({ doc, onBookmark, isBookmarked, isSaving }: { doc: { title: string; url: string; description?: string }; onBookmark: (item: BookmarkPayload) => void; isBookmarked: boolean; isSaving: boolean }) {
  return (
    <motion.div whileHover={{ y: -4 }} className="glass-card p-5 flex flex-col justify-between group">
      <div className="space-y-2">
        <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md">
          Docs
        </span>
        <h4 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors leading-snug">
          {doc.title}
        </h4>
        <p className="text-xs text-slate-400 line-clamp-2">
          {doc.description || 'Official technical documentation and learning resources.'}
        </p>
      </div>
      <div className="pt-4 border-t border-slate-800/80 mt-4 flex items-center justify-between gap-3">
        <span className="text-[10px] text-slate-500">Official Reference</span>
        <div className="flex items-center gap-3 shrink-0">
          <SaveButton onClick={() => onBookmark({ title: doc.title, url: doc.url, type: 'Document' })} isBookmarked={isBookmarked} isSaving={isSaving} />
          <a 
            href={doc.url} 
            target="_blank" 
            rel="noreferrer"
            className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5"
          >
            Open <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </motion.div>
  );
}
function EmptyState({ type }: { type: string }) {
  return (
    <div className="col-span-full text-center py-12 border border-dashed border-slate-800 rounded-2xl">
      <HelpCircle className="w-8 h-8 text-slate-600 mx-auto mb-3" />
      <p className="text-sm text-slate-500">No {type} found for this topic.</p>
    </div>
  );
}


