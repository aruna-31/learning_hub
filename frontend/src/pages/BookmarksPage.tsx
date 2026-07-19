import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Bookmark, Trash2, ExternalLink, HelpCircle, Search } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Resource {
  title: string;
  url: string;
  type: string;
  step_id: string;
}

interface BookmarkItem {
  id: string; // UUID
  resource_id: string;
  created_at: string;
  resource: Resource | null;
}

export default function BookmarksPage() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'title'>('newest');

  // 1. Fetch all bookmarks
  const { data, isLoading, error } = useQuery<{ items: BookmarkItem[] }>({
    queryKey: ['userBookmarks'],
    queryFn: async () => {
      const res = await apiClient.get('/bookmarks');
      return res.data;
    }
  });

  // 2. Delete bookmark mutation
  const removeBookmarkMutation = useMutation({
    mutationFn: async (bookmarkId: string) => {
      await apiClient.delete(`/bookmarks/${bookmarkId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userBookmarks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardMetrics'] });
      toast.success('Bookmark removed.');
    },
    onError: () => {
      toast.error('Failed to remove bookmark.');
    }
  });

  const handleRemove = (id: string) => {
    if (removeBookmarkMutation.isPending) return;
    if (confirm('Are you sure you want to remove this bookmarked resource?')) {
      removeBookmarkMutation.mutate(id);
    }
  };

  const getTagColor = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'video':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'repository':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
      case 'book':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
      case 'document':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'dataset':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-700/30';
    }
  };

  // Local Filter and Sort
  const filteredItems = (data?.items || [])
    .filter((item) => {
      const resource = item.resource;
      if (!resource) return false;
      const matchesSearch = 
        resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.url.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesType = 
        typeFilter === 'all' || 
        resource.type.toLowerCase() === typeFilter.toLowerCase();
      
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      if (sortBy === 'newest') {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      if (sortBy === 'oldest') {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }
      if (sortBy === 'title') {
        return (a.resource?.title || '').localeCompare(b.resource?.title || '');
      }
      return 0;
    });

  // Skeleton Card component
  const SkeletonCard = () => (
    <div className="glass-card p-5 space-y-4 animate-pulse">
      <div className="flex justify-between items-center">
        <div className="h-6 w-16 bg-slate-800 rounded-md" />
        <div className="h-6 w-6 bg-slate-800 rounded-full" />
      </div>
      <div className="h-4 bg-slate-800 rounded w-5/6" />
      <div className="pt-4 border-t border-slate-850 mt-4 flex justify-between">
        <div className="h-3 w-20 bg-slate-800 rounded" />
        <div className="h-3 w-16 bg-slate-800 rounded" />
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Bookmarks Manager <Bookmark className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Keep track of important videos, books, developer repositories, or study documents you saved during searches.
        </p>
      </div>

      {/* Control bar */}
      <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search saved resources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-550 focus-glow focus:outline-none"
          />
        </div>

        <div className="flex gap-3">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 text-slate-305 text-xs rounded-xl px-4 py-2.5 focus:outline-none cursor-pointer text-slate-300"
          >
            <option value="all">All Types</option>
            <option value="video">Videos</option>
            <option value="repository">Repositories</option>
            <option value="book">Books</option>
            <option value="document">Documentation</option>
            <option value="dataset">Datasets</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="bg-slate-900 border border-slate-800 text-slate-305 text-xs rounded-xl px-4 py-2.5 focus:outline-none cursor-pointer text-slate-300"
          >
            <option value="newest">Newest Added</option>
            <option value="oldest">Oldest Added</option>
            <option value="title">Alphabetical</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => <SkeletonCard key={i} />)}
        </div>
      ) : error ? (
        <div className="text-center py-10 bg-rose-500/10 border border-rose-500/20 rounded-2xl max-w-xl mx-auto">
          <p className="text-rose-400 font-semibold">Failed to fetch bookmarks</p>
        </div>
      ) : filteredItems.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {filteredItems.map((item) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95, y: 10 }}
                transition={{ duration: 0.2 }}
                whileHover={{ y: -4 }}
                className="glass-card p-5 flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-[10px] font-bold px-2.5 py-1 rounded-md border uppercase tracking-wider ${getTagColor(item.resource?.type)}`}>
                      {item.resource?.type || 'Resource'}
                    </span>
                    <button
                      onClick={() => handleRemove(item.id)}
                      className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition-colors"
                      title="Remove Bookmark"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-2 leading-snug">
                    {item.resource?.title || 'Untitled Resource'}
                  </h4>
                </div>

                <div className="pt-4 border-t border-slate-800/80 mt-4 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Added: {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  {item.resource?.url && (
                    <a
                      href={item.resource.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
                    >
                      Open Link <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <div className="text-center py-20 border border-dashed border-slate-800 rounded-2xl max-w-xl mx-auto">
          <HelpCircle className="w-10 h-10 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Bookmarks Found</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Try adjusting your search query or filters to find saved items, or search for a topic to bookmark resources.
          </p>
        </div>
      )}

    </div>
  );
}
