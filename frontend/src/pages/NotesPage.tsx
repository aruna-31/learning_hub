import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import { FileText, Save, Trash2, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface NoteItem {
  id: string; // UUID
  step_id: string; // UUID
  content: string;
  created_at: string;
  updated_at: string;
}

export default function NotesPage() {
  const queryClient = useQueryClient();
  const [selectedNote, setSelectedNote] = useState<NoteItem | null>(null);
  const [editorContent, setEditorContent] = useState('');

  // 1. Fetch all student notes
  const { data, isLoading, error } = useQuery<{ items: NoteItem[] }>({
    queryKey: ['userNotes'],
    queryFn: async () => {
      const res = await apiClient.get('/notes');
      return res.data;
    }
  });

  // 2. Update note mutation
  const updateNoteMutation = useMutation({
    mutationFn: async ({ noteId, content }: { noteId: string; content: string }) => {
      const res = await apiClient.put(`/notes/${noteId}`, { content });
      return res.data;
    },
    onSuccess: (updatedNote) => {
      queryClient.invalidateQueries({ queryKey: ['userNotes'] });
      setSelectedNote(updatedNote);
      toast.success('Note updated!');
    },
    onError: () => {
      toast.error('Failed to save changes.');
    }
  });

  // 3. Delete note mutation
  const deleteNoteMutation = useMutation({
    mutationFn: async (noteId: string) => {
      await apiClient.delete(`/notes/${noteId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userNotes'] });
      setSelectedNote(null);
      setEditorContent('');
      toast.success('Note deleted.');
    },
    onError: () => {
      toast.error('Failed to delete note.');
    }
  });

  const handleSelectNote = (note: NoteItem) => {
    setSelectedNote(note);
    setEditorContent(note.content);
  };

  const handleSave = () => {
    if (!selectedNote || !editorContent.trim() || updateNoteMutation.isPending) return;
    updateNoteMutation.mutate({ noteId: selectedNote.id, content: editorContent.trim() });
  };

  const handleDelete = () => {
    if (!selectedNote || deleteNoteMutation.isPending) return;
    if (confirm('Are you sure you want to delete this study note?')) {
      deleteNoteMutation.mutate(selectedNote.id);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Notes Workspace <FileText className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Review, edit, and update study summaries and personalized notes you attached to roadmap steps during your curriculum progression.
        </p>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <p className="text-sm text-slate-500">Loading your notes workspace...</p>
        </div>
      ) : error ? (
        <div className="text-center py-10 bg-rose-500/10 border border-rose-500/20 rounded-2xl max-w-xl mx-auto">
          <p className="text-rose-400 font-semibold">Failed to fetch notes</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch min-h-[500px]">
          
          {/* Left panel: Notes list */}
          <div className="glass-card p-5 space-y-4 flex flex-col justify-between max-h-[600px] overflow-y-auto">
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest px-1">Saved Summaries</h3>
              
              {data?.items && data.items.length > 0 ? (
                <div className="flex flex-col gap-2">
                  {data.items.map((note) => {
                    const isSelected = selectedNote?.id === note.id;
                    return (
                      <button
                        key={note.id}
                        onClick={() => handleSelectNote(note)}
                        className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-start gap-3 ${
                          isSelected 
                            ? 'bg-indigo-600/15 border-indigo-500/30 text-white' 
                            : 'bg-slate-900/40 border-slate-800 hover:border-slate-700/80 text-slate-300 hover:text-slate-200'
                        }`}
                      >
                        <FileText className={`w-4 h-4 mt-0.5 shrink-0 ${isSelected ? 'text-indigo-400' : 'text-slate-500'}`} />
                        <div className="min-w-0 flex-1">
                          <p className="text-xs text-slate-500 font-mono mb-1">
                            Updated: {new Date(note.updated_at).toLocaleDateString()}
                          </p>
                          <p className="text-sm font-medium truncate leading-tight">
                            {note.content.substring(0, 45) || 'Empty note content...'}
                          </p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-20 text-slate-500 text-sm">
                  No notes saved yet. Create a note from any roadmap timeline step!
                </div>
              )}
            </div>
          </div>

          {/* Right panel: Note Workspace Editor */}
          <div className="lg:col-span-2 glass-card p-6 md:p-8 flex flex-col justify-between space-y-6">
            {selectedNote ? (
              <div className="flex-1 flex flex-col justify-between space-y-4">
                
                {/* Editor Header */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" /> Workspace Active Note
                    </span>
                    <h4 className="text-sm font-semibold text-slate-400 truncate max-w-md">
                      Step ID: {selectedNote.step_id}
                    </h4>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleDelete}
                      disabled={deleteNoteMutation.isPending}
                      className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-500/10 transition-colors"
                      title="Delete Note"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={updateNoteMutation.isPending}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 text-white rounded-lg text-xs font-semibold shadow-md transition-colors flex items-center gap-1.5"
                    >
                      {updateNoteMutation.isPending ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <>
                          <Save className="w-3.5 h-3.5" /> Save Changes
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Text Editor area */}
                <div className="flex-1 flex flex-col min-h-[300px]">
                  <textarea
                    placeholder="Start typing your study summaries or markdown cheat-sheet notes here..."
                    value={editorContent}
                    onChange={(e) => setEditorContent(e.target.value)}
                    className="w-full flex-1 bg-slate-950/40 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-650 focus-glow text-sm resize-none font-sans leading-relaxed"
                  />
                </div>

                <div className="text-[10px] text-slate-600 text-right">
                  Auto-save state active. Changes must be committed by clicking Save.
                </div>

              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <AlertCircle className="w-12 h-12 text-slate-700 mb-4" />
                <h3 className="text-lg font-bold text-white mb-2">No Note Selected</h3>
                <p className="text-sm text-slate-500 max-w-sm">
                  Select a note from the left sidebar summaries column to open it in the editor.
                </p>
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
